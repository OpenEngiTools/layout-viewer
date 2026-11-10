# layout-viewer-core

Interactive 2D PCB layout viewer built on PySide6 and Qt RHI (Direct3D 11, Vulkan, Metal).

The package renders detached `LayoutScene` values and is independent of source applications.

```python
from layout_viewer_core import show_scene
from layout_viewer_core.demo import demo_scene

show_scene(demo_scene())
```

## Create a scene

Build a scene from layers and geometry, then pass it to `show_scene`:

```python
from layout_viewer_core import LayoutScene, SceneLayer, ScenePolygon, SceneTrace, show_scene

scene = LayoutScene(
    layers=(SceneLayer("F.Cu", (0.95, 0.61, 0.20, 1.0)),),
    polygons=(
        ScenePolygon(
            object_id=1,
            layer="F.Cu",
            net="GND",
            exterior=((0, 0), (40, 0), (40, 25), (0, 25)),
        ),
    ),
    title="My board",
    traces=(SceneTrace(2, "F.Cu", "SIGNAL", (5, 5), (30, 15), 0.5),),
)

show_scene(scene)
```

Run the synthetic demo board:

```bash
python -m layout_viewer_core
```

## Architecture

- Core scene and geometry logic lives in `src/layout_viewer_core/` (`scene.py`, `mesh.py`,
  `picking.py`, and `camera.py`) and does not depend on Qt.
- `qt/app.py` bootstraps the application. Qt UI code is grouped in `qt/ui/`;
  canvas and GPU rendering code is grouped in `qt/render/`.
- UI SVG assets live in `qt/ui/assets/`. Rendering shaders and their compiled
  packs live in `qt/render/shaders/`.
- `demo.py` builds a synthetic scene for trying the viewer without an external data source.

For the data flow, module responsibilities, development setup, tests, and common
troubleshooting, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development

Install the checkout and its runtime dependencies into the active environment:

```bash
python -m pip install -e .
```

Wheel and editable builds compile the RHI shaders in `src/layout_viewer_core/qt/render/shaders`
with the Qt `qsb` tool shipped by PySide6 (or the executable named by `LAYOUT_VIEWER_QSB`).
After editing shader sources in a checkout, refresh the local packs with:

```bash
python tools/bake_viewer_shaders.py
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).