import importlib.util
import sys
from pathlib import Path
import typer
from typing_extensions import Annotated

from psim.model import Model
from psim.viewer.main import launch_viewer, HAVE_PYSIDE6

# Create a Typer application
app = typer.Typer(
    name="psim",
    help="Run a simulation from a model file.",
    add_completion=False,
    invoke_without_command=True, # Allows the callback to be the main command
)

def _find_model_in_module(module) -> Model | None:
    """Finds the first psim.Model instance in a given module."""
    for obj in vars(module).values():
        if isinstance(obj, Model):
            return obj
    return None

def _load_model_from_file(model_file: Path) -> Model | None:
    """Loads a psim.Model from a Python file."""
    if not model_file.exists():
        print(f"Error: Model file not found at {model_file}")
        raise typer.Exit(code=1)

    module_dir = model_file.parent.resolve()
    sys.path.insert(0, str(module_dir))

    try:
        spec = importlib.util.spec_from_file_location(model_file.stem, model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading model file: {e}")
        raise typer.Exit(code=1)
    finally:
        sys.path.pop(0)

    model_instance = _find_model_in_module(module)
    if not model_instance:
        print(f"Error: No 'psim.Model' instance found in {model_file}")
        raise typer.Exit(code=1)

    return model_instance


@app.callback()
def run(
    model_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="The path to the Python file containing the simulation model.",
        ),
    ],
    until: Annotated[
        float,
        typer.Option("-u", "--until", help="Simulation end time. Overrides model settings."),
    ] = None,
    seed: Annotated[
        int,
        typer.Option("-s", "--seed", help="Random seed. Overrides model settings."),
    ] = None,
    gui: Annotated[
        bool,
        typer.Option("--gui/--no-gui", help="Launch the GUI viewer or run in headless mode."),
    ] = True,
):
    """
    psim: A Python-based discrete-event simulation tool.
    """
    model_instance = _load_model_from_file(model_file)

    if until is not None:
        model_instance.until = until
        typer.echo(f"Overriding simulation end time: --until {until}")
    if seed is not None:
        model_instance.seed = seed
        typer.echo(f"Overriding simulation seed: --seed {seed}")

    if gui:
        if not HAVE_PYSIDE6:
            typer.secho(
                "Cannot launch GUI because PySide6 is not installed.", fg=typer.colors.RED
            )
            typer.echo("Hint: Install with 'pip install \"psim[gui]\"'")
            raise typer.Exit(code=1)

        typer.echo("Launching GUI viewer...")
        launch_viewer(model_instance)
    else:
        if hasattr(model_instance.tracer, "message_logged"):
             model_instance.tracer.message_logged.connect(
                lambda time, msg: typer.echo(f"{time:.2f}: {msg}")
            )

        typer.echo(f"Running model from '{model_file}' in headless mode...")
        model_instance.run()
        typer.secho("✅ Simulation run complete.", fg=typer.colors.GREEN)


main = app

if __name__ == "__main__":
    app()
