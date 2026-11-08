from dataclasses import dataclass
from threading import RLock

import pytest

from layout_viewer.capture import SourceCapture
from layout_viewer.scene import LayoutScene, SceneLayer, SceneObjectInfo, ScenePolygon


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


def _scene(*polygons: ScenePolygon, infos=()) -> LayoutScene:
    return LayoutScene(
        (SceneLayer("F.Cu", (1, 0, 0, 1)),),
        polygons,
        object_info=infos,
    )


def _polygon(object_id: int, x: float) -> ScenePolygon:
    return ScenePolygon(object_id, "F.Cu", None, ((x, 0), (x + 1, 0), (x + 1, 1), (x, 1)))


def test_full_capture_records_scene_revision_and_delta_replaces_changed_objects() -> None:
    original, removed, untouched = _polygon(1, 0), _polygon(2, 3), _polygon(3, 6)
    replacement = _polygon(1, 10)
    changes = ChangeJournal()
    full_loader_calls = []
    delta_loader_calls = []
    source = SourceCapture(
        lambda progress, **kwargs: (full_loader_calls.append(progress) or _scene(original, removed, untouched)),
        changes=changes,
        delta_loader=lambda delta, previous, progress: (
            delta_loader_calls.append(delta) or _scene(replacement, infos=(SceneObjectInfo(1, "zone"),))
        ),
    )

    initial = source.capture(full=True)
    source.revision = initial.revision
    assert initial.scene.polygons == (original, removed, untouched)
    assert initial.revision == 1

    changes.revision = 2
    changes.delta = Delta(2, upserts=((1, object()),), removed=frozenset({1, 2}))
    updated = source.capture(previous=initial.scene)

    assert full_loader_calls == [None]
    assert len(delta_loader_calls) == 1
    assert updated.revision == 2
    assert updated.changed == frozenset({1, 2})
    assert updated.scene.polygons == (untouched, replacement)
    assert updated.scene.polygons[0] is untouched
    assert updated.scene.object_info == (SceneObjectInfo(1, "zone"),)


def test_empty_delta_reuses_previous_scene_without_loading() -> None:
    previous = _scene(_polygon(1, 0))
    changes = ChangeJournal()
    changes.delta = Delta(2)
    source = SourceCapture(
        lambda *args, **kwargs: pytest.fail("full loader should not run"),
        changes=changes,
        delta_loader=lambda *args: pytest.fail("delta loader should not run"),
    )
    source.revision = 1

    result = source.capture(previous=previous)

    assert result.scene is previous
    assert result.revision == 2
    assert result.changed == frozenset()


def test_full_delta_falls_back_to_full_loader() -> None:
    replacement = _polygon(1, 7)
    changes = ChangeJournal()
    changes.revision = 3
    changes.delta = Delta(3, full=True)
    source = SourceCapture(lambda *args, **kwargs: _scene(replacement), changes=changes)

    result = source.capture(previous=_scene(_polygon(1, 0)))

    assert result.revision == 3
    assert result.scene.polygons == (replacement,)


def test_closed_source_is_reported() -> None:
    changes = ChangeJournal()
    changes.closed = True
    source = SourceCapture(lambda *args, **kwargs: _scene(), changes=changes)

    with pytest.raises(RuntimeError, match="source session is closed"):
        source.capture()


def test_capture_failure_does_not_advance_committed_revision() -> None:
    changes = ChangeJournal()
    source = SourceCapture(
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("capture failed")),
        changes=changes,
    )
    source.revision = 1
    changes.revision = 2

    with pytest.raises(ValueError, match="capture failed"):
        source.capture(full=True)

    assert source.revision == 1
