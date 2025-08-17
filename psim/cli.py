import argparse
import importlib.util
import sys
from pathlib import Path

from psim.model import Model

def find_model_in_module(module) -> Model | None:
    """Finds the first psim.Model instance in a given module."""
    for obj in vars(module).values():
        if isinstance(obj, Model):
            return obj
    return None

from psim.viewer.main import launch_viewer

def run_simulation(args):
    """The logic for the 'run' command."""
    model_file = Path(args.model_file)
    if not model_file.exists():
        print(f"Error: Model file not found at {model_file}")
        sys.exit(1)

    # Add the model file's directory to the Python path
    module_dir = model_file.parent.resolve()
    sys.path.insert(0, str(module_dir))

    try:
        spec = importlib.util.spec_from_file_location(model_file.stem, model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)

    model_instance = find_model_in_module(module)
    if not model_instance:
        print(f"Error: No 'psim.Model' instance found in {model_file}")
        sys.exit(1)

    # Override model parameters from CLI arguments
    if args.until is not None:
        model_instance.until = args.until
        print(f"Overriding simulation end time: --until {args.until}")
    if args.seed is not None:
        model_instance.seed = args.seed
        print(f"Overriding simulation seed: --seed {args.seed}")

    if args.gui:
        print("Launching GUI viewer...")
        launch_viewer(model_instance)
    else:
        # In headless mode, connect a simple logger to the tracer for console output
        model_instance.tracer.message_logged.connect(
            lambda time, msg: print(f"{time:.2f}: {msg}")
        )
        print(f"Running model from '{model_file}'...")
        model_instance.run()
        print("✅ Simulation run complete.")

def main():
    """The main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="psim: A Python-based discrete-event simulation tool.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # --- Run Command ---
    parser_run = subparsers.add_parser("run", help="Run a simulation from a model file.")
    parser_run.add_argument("model_file", help="The path to the Python file containing the simulation model.")
    parser_run.add_argument("-u", "--until", type=float, help="Simulation end time. Overrides model settings.")
    parser_run.add_argument("-s", "--seed", type=int, help="Random seed. Overrides model settings.")
    parser_run.add_argument("--gui", action="store_true", help="Launch the GUI viewer.")
    parser_run.set_defaults(func=run_simulation)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
