
"""Interactive 2D PCB layout viewer. Importing this module does not load Qt."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from layout_viewer.picking import PickedObject
from layout_viewer.scene import (
    LayoutScene,
    SceneComponent,
    SceneJoin,
    SceneLayer,
    SceneObjectInfo,
    ScenePad,
    ScenePolygon,
    SceneTrace,
)

if TYPE_CHECKING:
    from layout_viewer.qt.window import LayoutWindow

__version__ = "0.1.0"

__all__ = [
    "LayoutScene",
    "PickedObject",
    "SceneComponent",
    "SceneJoin",
    "SceneLayer",
    "SceneObjectInfo",
    "ScenePad",
    "ScenePolygon",
    "SceneTrace",
    "show_scene",
]


def show_scene(scene: LayoutScene | None = None, **options: Any) -> LayoutWindow:
    """Open a layout window; see :func:`layout_viewer.qt.app.show_scene` for options."""
    try:
        from layout_viewer.qt.app import show_scene as show
    except ImportError as exc:
        raise ImportError("The layout viewer requires PySide6 and mapbox-earcut: pip install layout-viewer.") from exc
    return show(scene, **options)