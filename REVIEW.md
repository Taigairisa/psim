# Project Review

## Test Coverage
- `psim.core` and probability distributions have unit tests.
- No tests for buffer, process, sink, source blocks, tracer, CLI, or viewer modules.
- Integration test covers only a simple Source → Process → Sink scenario; no coverage for failure paths, warm‑up periods, or complex networks.
- Tests cannot run in a fresh environment because the package is not installable without network access and requires `PySide6` during import.

## Functional Requirements
- README lists many blocks (Router, Delay, Conveyor, etc.) and features (warmup, multiple replications), but repository only implements Source, Process, Buffer, Sink.
- Future Event List and simulation basics are present, but no resource management, metrics, or export features yet.
- CLI exposes `run` command, but no tests or documentation for additional options (e.g., `--gui`, `--export`).

## Non‑Functional Requirements
- Non-functional goals like reproducibility and performance are mentioned, but no benchmarks or automated checks are present.
- Viewer relies on `PySide6`, making headless environments hard to support; consider optional import or plugin architecture.

## Dependencies & Build
- `pyproject.toml` lists `typer[all]` and `pyside6`; installing dependencies fails offline, blocking test execution.
- Consider separating GUI dependencies from core package to lighten installation and testing.

## Recommendations
- Add unit tests for buffer, process, sink, source, and tracer logic.
- Provide mocks or optional imports for GUI components to enable core tests without `PySide6`.
- Clarify implementation roadmap in README versus current scope to avoid expectation gaps.
- Include instructions or scripts for installing dependencies and running tests locally.
