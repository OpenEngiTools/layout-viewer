from dataclasses import dataclass
from threading import RLock

from layout_viewer_core.capture import SourceCapture
from layout_viewer_core.mesh import prepare_scene
from layout_viewer_core.qt.ui.window import _Prepare
from layout_viewer_core.scene import LayoutScene, SceneLayer, SceneObjectInfo, ScenePolygon


@dataclass
class Delta:
    revision: int
    upserts: tuple = ()
    removed: frozenset = frozenset()
    full: bool = False


class ChangeJournal:
    def __init__(self) -> None:
        self.lock = RLock()
        self.revision = 1
        self.closed = False
        self.delta = Delta(1, full=True)

    def since(self, revision: int) -> Delta:
        return self.delta


def _polygon(object_id: int, x: float) -> ScenePolygon:
    return ScenePolygon(object_id, "F.Cu", "GND", ((x, 0), (x + 2, 0), (x + 2, 2), (x, 2)))


def _scene(*polygons: ScenePolygon, infos=None) -> LayoutScene:
    return LayoutScene(
        (SceneLayer("F.Cu", (1, 0, 0, 1)),),
        polygons,
        object_info=(
            tuple(SceneObjectInfo(item.object_id, "zone", item.net) for item in polygons) if infos is None else infos
        ),
    )


def _run_prepare(preparation: _Prepare):
    results = {}
    preparation.signals.scene_ready.connect(lambda scene: results.__setitem__("scene", scene))
    preparation.signals.ready.connect(lambda prepared: results.__setitem__("prepared", prepared))
    preparation.signals.failed.connect(lambda error: results.__setitem__("error", error))
    preparation.run()
    assert "error" not in results, results.get("error")
    return results["scene"], results["prepared"]


def test_incremental_source_refresh_updates_scene_mesh_and_picking() -> None:
    original, unchanged = _polygon(1, 0), _polygon(2, 5)
    replacement = _polygon(1, 10)
    changes = ChangeJournal()
    full_calls = []
    source = SourceCapture(
        lambda *args, **kwargs: (full_calls.append(True) or _scene(original, unchanged)),
        changes=changes,
        delta_loader=lambda delta, previous, progress: _scene(
            replacement,
            infos=(SceneObjectInfo(1, "zone", "GND"),),
        ),
    )

    initial_scene, initial_prepared = _run_prepare(_Prepare(_scene(), source, previews=False))
    source.revision = changes.revision
    changes.revision = 2
    changes.delta = Delta(2, upserts=((1, object()),), removed=frozenset({1}))

    updated_scene, updated_prepared = _run_prepare(
        _Prepare(
            initial_scene,
            source,
            previews=False,
            incremental=True,
            previous=(initial_scene, initial_prepared),
        )
    )

    assert full_calls == [True]
    assert updated_scene is not initial_scene
    assert updated_scene.polygons == (unchanged, replacement)
    assert updated_scene.polygons[0] is unchanged
    assert updated_prepared.mesh_parent_id == id(initial_prepared)
    assert updated_prepared.picking.pick((11, 1), 100, {"F.Cu"}).object.info.object_id == 1
    assert updated_prepared.picking.pick((1, 1), 100, {"F.Cu"}) is None
