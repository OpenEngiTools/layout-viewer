
"""Launch the synthetic demo board with ``python -m layout_viewer``."""

from __future__ import annotations

import argparse
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Interactive PySide6/RHI 2D layout viewer demo")
    parser.add_argument(
        "--backend",
        choices=("auto", "vulkan", "d3d11", "metal"),
        default=None,
        help="Graphics API (default: platform native)",
    )
    parser.add_argument("--color-by-layer", action="store_false", dest="color_by_net", help="Use source layer colors")
    args = parser.parse_args(argv)
    from layout_viewer import show_scene
    from layout_viewer.demo import demo_scene

    show_scene(demo_scene(), color_by_net=args.color_by_net, backend=args.backend)


if __name__ == "__main__":
    main()