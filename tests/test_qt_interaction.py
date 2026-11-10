from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from layout_viewer_core.mesh import prepare_scene
from layout_viewer_core.qt.view.canvas import LayoutView


def test_canvas_click_selects_and_escape_clears_selection(qapp, sample_scene) -> None:
    canvas = LayoutView(sample_scene, backend="vulkan")
    canvas.resize(200, 200)
    canvas.camera.resize(200, 200)
    canvas.camera.center_x = canvas.camera.center_y = 5
    canvas.camera.scale = 10
    canvas.visible_layers = {"F.Cu"}
    canvas.set_prepared(prepare_scene(sample_scene))
    selected = []
    canvas.selection_changed.connect(selected.append)

    QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))

    assert canvas.selection is not None
    assert canvas.selection.object.info.object_id == 1
    assert selected[-1].object_id == 1

    QTest.keyClick(canvas, Qt.Key.Key_Escape)

    assert canvas.selection is None
    assert selected[-1] is None
    canvas.cleanup()


def test_canvas_pick_tool_can_be_disabled(qapp, sample_scene) -> None:
    canvas = LayoutView(sample_scene, backend="vulkan")
    canvas.camera.resize(200, 200)
    canvas.camera.center_x = canvas.camera.center_y = 5
    canvas.camera.scale = 10
    canvas.set_prepared(prepare_scene(sample_scene))
    canvas.set_pick_enabled(False)

    assert canvas.pick_at(100, 100) is None
    assert canvas.selection is None
    canvas.cleanup()


def test_canvas_pick_respects_visible_layer_and_network_filters(qapp, sample_scene) -> None:
    canvas = LayoutView(sample_scene, backend="vulkan")
    canvas.camera.resize(200, 200)
    canvas.camera.center_x = canvas.camera.center_y = 5
    canvas.camera.scale = 10
    canvas.set_prepared(prepare_scene(sample_scene))
    canvas.net = "SIG"
    canvas.visible_layers = {"F.Cu"}

    assert canvas.pick_at(100, 100) is None
    canvas.net = "GND"
    assert canvas.pick_at(100, 100).object.info.object_id == 1
    canvas.visible_layers = {"B.Cu"}
    assert canvas.pick_at(100, 100) is None
    canvas.cleanup()


def test_canvas_zoom_changes_camera_scale(qapp, sample_scene) -> None:
    canvas = LayoutView(sample_scene, backend="vulkan")
    canvas.resize(200, 200)
    canvas.camera.resize(200, 200)
    initial_scale = canvas.camera.scale

    canvas.zoom(1.5)

    assert canvas.camera.scale == initial_scale * 1.5
    canvas.cleanup()
