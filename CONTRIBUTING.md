# Contributing

This guide is a quick map of the codebase and the usual local development loop.

## Get started

From the repository root, install the package and test dependencies:

```bash
uv sync --extra test
```

Run the demo using the platform's default graphics backend:

```bash
uv run python -m layout_viewer_core
```

On macOS, `--backend metal` is also available; on Windows, use `--backend d3d11`.
Vulkan is available where its runtime and driver are installed.

Run the tests:

```bash
uv run pytest
```

For headless environments, run Qt tests with the offscreen platform:

```bash
QT_QPA_PLATFORM=offscreen uv run pytest
```

## How a scene is rendered

```text
External source callback or demo
        │
        ▼
    LayoutScene              immutable, detached PCB data
        │
        ▼
    prepare_scene             triangulation, render batches, picking data
        │
        ▼
    LayoutWindow ──────────── UI, controls, asynchronous scene preparation
        │
        ▼
    LayoutView / canvas       navigation, selection, overlays
        │
        ▼
    Renderer + Qt RHI         GPU resources, shader passes, drawing
```

The viewer consumes a detached `LayoutScene`; it does not own or query the
upstream data source. `prepare_scene` converts that model to a `PreparedScene`. The window
coordinates preparation and user controls, the canvas connects interaction to
rendering, and the renderer uploads and draws prepared geometry. Picking data is
prepared alongside the render data so selection does not need to access the source.

## Module map

| Area | Modules | Responsibility |
| --- | --- | --- |
| Scene and geometry | `scene.py`, `mesh.py`, `picking.py`, `camera.py` | Scene values and validation, CPU geometry preparation, object picking, and camera transforms |
| Scene updates | `capture.py`, `incremental.py`, `progress.py` | Capture/update support, incremental preparation, and progress reporting |
| Qt startup | `qt/app.py`, `__main__.py` | QApplication lifecycle, public window launch, and demo CLI |
| Qt UI | `qt/ui/window.py`, `panels.py`, `inspector.py`, `navigation.py`, `loading.py`, `theme.py`, `icons.py` | Window orchestration and user-facing controls |
| Qt rendering | `qt/render/canvas.py`, `renderer.py`, `rhi.py`, `coverage.py`, `grid.py`, `component_labels.py` | Canvas interaction, GPU resources, render passes, overlays, and labels |
| Rendering resources | `qt/render/shaders/` | Shader sources, compiled `.qsb` packs, and third-party notices |
| UI resources | `qt/ui/assets/` | SVG assets used by the Qt stylesheets |
| Demo | `demo.py` | Synthetic scene for development without an external data source |
| Build tooling | `_build_backend/`, `tools/bake_viewer_shaders.py` | Build hooks and local shader-pack generation |

## Dependency boundaries

- Keep the scene model, camera, mesh preparation, and picking independent of Qt
  and external data sources. They should operate on ordinary Python data and detached scene values.
- Keep source/session integration outside the renderer. Pass captured geometry
  into the viewer as a `LayoutScene`.
- The Qt UI may compose the canvas and render-facing controls. The renderer
  should not depend on the main window or UI panels.
- Keep shader compilation in build tooling; runtime rendering loads the packaged
  shader packs.
- When moving a module or resource, update its imports, runtime resource lookup,
  build-time paths, and tests together.

## Tests and shader changes

The tests in `tests/` currently smoke-test Qt theme resources and compiled shader
packs. Add focused tests for geometry, picking, and scene invariants when changing
those areas.

Shader source files live in `src/layout_viewer_core/qt/render/shaders/`. After editing
them, regenerate the local packs:

```bash
uv run python tools/bake_viewer_shaders.py
```

Wheel and editable builds also compile shader packs. `LAYOUT_VIEWER_QSB` can point to a
specific Qt `qsb` executable when the build environment needs a non-default
compiler.

If the viewer reports that shader packs are missing, regenerate them with the
command above. If it reports that the renderer could not initialize, check the
selected backend and the machine's graphics driver/desktop session; a headless
test environment cannot validate an interactive GPU renderer.
