from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from layout_viewer.scene import LayoutScene, SceneLayer, SceneObjectInfo, ScenePad, ScenePolygon, SceneTrace


@pytest.fixture
def sample_scene() -> LayoutScene:
    return LayoutScene(
        layers=(
            SceneLayer("F.Cu", (1.0, 0.0, 0.0, 1.0)),
            SceneLayer("B.Cu", (0.0, 0.0, 1.0, 1.0)),
        ),
        polygons=(ScenePolygon(1, "F.Cu", "GND", ((0, 0), (10, 0), (10, 10), (0, 10))),),
        traces=(SceneTrace(2, "F.Cu", "SIG", (12, 2), (18, 2), 1),),
        pads=(ScenePad(3, "B.Cu", "GND", (20, 5), (2, 2)),),
        object_info=(
            SceneObjectInfo(1, "zone", "GND"),
            SceneObjectInfo(2, "trace", "SIG"),
            SceneObjectInfo(3, "pad", "GND"),
        ),
    )


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])
