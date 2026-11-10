from __future__ import annotations

import os
import re
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QWidget

from layout_viewer_core.qt.ui.theme import apply_viewer_theme


def test_theme_uses_available_font_and_existing_assets() -> None:
    """Prevent missing-font and moved-SVG regressions when applying the Qt theme."""
    application = QApplication.instance() or QApplication([])
    assert application is not None

    window = QWidget()
    apply_viewer_theme(window)

    font_families = QFontDatabase.families()
    assert window.font().family() in font_families
    fixed_font_family = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
    assert fixed_font_family in window.styleSheet()

    asset_paths = re.findall(r'url\("([^"]+\.svg)"\)', window.styleSheet())
    assert asset_paths, "The viewer stylesheet should reference SVG assets."
    for asset_path in asset_paths:
        assert Path(asset_path).is_file(), f"Missing SVG asset: {asset_path}"
