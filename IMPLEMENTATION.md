# Implementation Overview

This document summarizes the planned architecture and key components of **psim** as described in the README.

## Core (`psim.core`)
- Event scheduler based on a Future Event List (min-heap) with a virtual clock (`now`) and `schedule(event, at)` API.
- Dedicated random number streams per block to improve reproducibility.
- Time advances by jumping to the next event; viewer throttles real-time speed.

## Model (`psim.model`)
- Holds nodes, edges, calendars, and initial inventory.
- Abstract `Node` base class provides hooks such as `on_enter(entity)`, `on_exit(entity)`, and `on_event(evt)`.
- Connections handled through a `Port` concept (`out_port -> in_port`).

## Blocks (`psim.blocks`)
- Includes `Source`, `Sink`, `Process`, `Buffer`, `Conveyor`, `Router`, `Batch`, `Failure`, and more.

## Metrics (`psim.metrics`)
- Tracks WIP, throughput, utilization, delays, and stockout rates via sampling or event-based integration.

## Viewer (`psim.viewer`)
- Decoupled from the core via pub-sub or in-process observers.
- Supports real-time factor control (`--speed 1x/10x/∞`), with `∞` executing as fast as possible while dropping frames.
- Minimal UI offers Start/Stop/Step, simulation time display, FPS/RTF, and optional overlays.

## CLI
- `psim run <model.py>` launches simulations with arguments for speed, end time, seed, and more.
- Optional `--export` generates KPI reports (CSV/Parquet) and event traces.

## Non-Functional Requirements
- High throughput in headless mode; viewer side controls real-time factor.
- Reproducible results via fixed random seeds and documented ordering for parallel replications.
- Extensible through low-coupled Observer/Plugin patterns for adding blocks, distributions, and KPIs.
- Portable across Windows, Linux, and macOS with a PySide6/DearPyGui-based GUI.
- Emphasizes unit tests, analytical model validation, regression tests, and profiling hooks for observability.

