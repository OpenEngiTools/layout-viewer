# layout-viewer

Interactive 2D PCB layout viewer built on PySide6 and Qt RHI (Direct3D 11, Vulkan, Metal).

The package renders detached `LayoutScene` values and has no EDB dependency. PyEDB
supplies scenes from EDB sessions through `pyedb.viewer_adapter` (`pip install "pyedb[viewer]"`).

```python
from layout_viewer import show_scene
from layout_viewer.demo import demo_scene

show_scene(demo_scene())
```

Run the synthetic demo board:

```bash
python -m layout_viewer --backend vulkan
```

## Architecture

- Core scene and geometry logic lives in `src/layout_viewer/` (`scene.py`, `mesh.py`,
  `picking.py`, and `camera.py`) and does not depend on Qt.
- `qt/app.py` bootstraps the application. Qt UI code is grouped in `qt/ui/`;
  canvas and GPU rendering code is grouped in `qt/render/`.
- UI SVG assets live in `qt/ui/assets/`. Rendering shaders and their compiled
  packs live in `qt/render/shaders/`.
- `demo.py` builds a synthetic scene for trying the viewer without an EDB session.

## Development

Install the checkout and its runtime dependencies into the active environment:

```bash
python -m pip install -e .
```

Wheel and editable builds compile the RHI shaders in `src/layout_viewer/qt/render/shaders`
with the Qt `qsb` tool shipped by PySide6 (or the executable named by `PYEDB_QSB`).
After editing shader sources in a checkout, refresh the local packs with:

```bash
python tools/bake_viewer_shaders.py
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).