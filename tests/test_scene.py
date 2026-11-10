from dataclasses import FrozenInstanceError

import pytest

from layout_viewer_core.scene import LayoutScene, SceneLayer, ScenePolygon


def test_scene_normalizes_collections_and_reports_geometry_bounds(sample_scene) -> None:
    assert isinstance(sample_scene.layers, tuple)
    assert isinstance(sample_scene.polygons, tuple)
    assert tuple(item.object_id for item in sample_scene.geometry) == (1, 2, 3)
    assert sample_scene.bounds == (0.0, 0.0, 21.0, 10.0)


def test_scene_is_immutable(sample_scene) -> None:
    with pytest.raises(FrozenInstanceError):
        sample_scene.title = "changed"


def test_scene_rejects_duplicate_layers() -> None:
    layer = SceneLayer("F.Cu", (1, 0, 0, 1))
    with pytest.raises(ValueError, match="unique"):
        LayoutScene((layer, layer), ())


def test_scene_rejects_geometry_on_unknown_layer() -> None:
    polygon = ScenePolygon(1, "missing", None, ((0, 0), (1, 0), (1, 1)))
    with pytest.raises(ValueError, match="Every object"):
        LayoutScene((SceneLayer("F.Cu", (1, 0, 0, 1)),), (polygon,))


def test_empty_scene_has_no_bounds() -> None:
    assert LayoutScene((), ()).bounds is None
