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

## Development

Wheel and editable builds compile the RHI shaders in `src/layout_viewer/qt/shaders`
with the Qt `qsb` tool shipped by PySide6 (or the executable named by `PYEDB_QSB`).
After editing shader sources in a checkout, refresh the local packs with:

```bash
python tools/bake_viewer_shaders.py
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).