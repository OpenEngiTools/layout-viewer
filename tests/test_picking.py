from layout_viewer.picking import PickIndex
from layout_viewer.scene import LayoutScene, SceneLayer, ScenePolygon


def test_pick_index_applies_layer_network_and_opacity_filters(sample_scene) -> None:
    index = PickIndex(sample_scene)

    assert index.pick((5, 5), 100, {"F.Cu"}).object.info.object_id == 1
    assert index.pick((5, 5), 100, {"B.Cu"}) is None
    assert index.pick((5, 5), 100, {"F.Cu"}, net="SIG") is None
    assert index.pick((5, 5), 100, {"F.Cu"}, net="GND").object.info.kind == "zone"
    assert index.pick((5, 5), 100, {"F.Cu"}, opacity=0) is None


def test_pick_index_picks_trace_and_pad(sample_scene) -> None:
    index = PickIndex(sample_scene)

    trace = index.pick((15, 2), 100, {"F.Cu"})
    pad = index.pick((20, 5), 100, {"B.Cu"})

    assert trace is not None and trace.object.info.object_id == 2
    assert pad is not None and pad.object.info.object_id == 3


def test_pick_index_does_not_pick_inside_polygon_hole() -> None:
    scene = LayoutScene(
        (SceneLayer("F.Cu", (1, 0, 0, 1)),),
        (
            ScenePolygon(
                7,
                "F.Cu",
                None,
                ((0, 0), (10, 0), (10, 10), (0, 10)),
                holes=(((4, 4), (6, 4), (6, 6), (4, 6)),),
            ),
        ),
    )
    index = PickIndex(scene)

    assert index.pick((2, 2), 100, {"F.Cu"}) is not None
    assert index.pick((5, 5), 100, {"F.Cu"}) is None


def test_empty_pick_index_returns_no_hit() -> None:
    index = PickIndex(LayoutScene((), ()))
    assert index.pick((0, 0), 1, set()) is None
