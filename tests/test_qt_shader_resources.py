from __future__ import annotations

from PySide6.QtGui import QShader

from layout_viewer.qt.render.rhi import SHADER_DIRECTORY


def test_shader_packs_load_from_qt_shader_directory() -> None:
    """Keep the renderer's shader lookup aligned with the package directory layout."""
    shader_packs = tuple(SHADER_DIRECTORY.glob("*.qsb"))
    assert shader_packs, f"No compiled shader packs found in {SHADER_DIRECTORY}"

    for path in shader_packs:
        shader = QShader.fromSerialized(path.read_bytes())
        assert shader.isValid(), f"Invalid shader pack: {path.name}"
