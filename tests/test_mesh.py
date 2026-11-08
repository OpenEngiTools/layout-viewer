import numpy as np

from layout_viewer.mesh import prepare_scene
from layout_viewer.scene import LayoutScene


def test_prepare_scene_builds_polygon_and_analytic_geometry(sample_scene) -> None:
    prepared = prepare_scene(sample_scene)

    assert len(prepared.batches) == 1
    assert prepared.batches[0].object_id == 1
    assert prepared.batches[0].ring_sizes == (4,)
    assert len(prepared.vertices) == 4
    assert len(prepared.indices) == 6
    assert prepared.instances.shape == (2, 40)
    assert prepared.picking is not None
    assert prepared.picking.pick((5, 5), 100, {"F.Cu"}).object.info.object_id == 1
    assert not prepared.sdf_sources.flags.writeable


def test_prepare_scene_reports_progress_and_supports_empty_scene() -> None:
    progress = []
    prepared = prepare_scene(LayoutScene((), ()), progress=lambda *event: progress.append(event))

    assert prepared.vertices.shape == (0, 4)
    assert prepared.indices.dtype == np.uint32
    assert prepared.instances.shape == (0, 40)
    assert prepared.picking.pick((0, 0), 1, set()) is None
    assert progress[-1][1:] == (1, 1)
