# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""PyEDB materials shared by the CPU copper pass and GPU analytic primitives."""

from __future__ import annotations

# Matplotlib CSS4 network palette, kept local so the frontend has no pyedb dependency.
_CSS4_COLORS = {
    "chocolate": "#D2691E",
    "darkgreen": "#006400",
    "orangered": "#FF4500",
    "darkseagreen": "#8FBC8F",
    "darkmagenta": "#8B008B",
    "saddlebrown": "#8B4513",
    "mediumaquamarine": "#66CDAA",
    "limegreen": "#32CD32",
    "blue": "#0000FF",
    "mediumseagreen": "#3CB371",
    "peru": "#CD853F",
    "turquoise": "#40E0D0",
    "darkcyan": "#008B8B",
    "olivedrab": "#6B8E23",
    "cyan": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "powderblue": "#B0E0E6",
    "hotpink": "#FF69B4",
    "palegreen": "#98FB98",
    "darkturquoise": "#00CED1",
    "magenta": "#FF00FF",
    "slateblue": "#6A5ACD",
    "lightgreen": "#90EE90",
    "sienna": "#A0522D",
    "darkorchid": "#9932CC",
    "orange": "#FFA500",
    "forestgreen": "#228B22",
    "palegoldenrod": "#EEE8AA",
    "blueviolet": "#8A2BE2",
    "royalblue": "#4169E1",
    "teal": "#008080",
    "darkgoldenrod": "#B8860B",
    "lightskyblue": "#87CEFA",
    "lime": "#00FF00",
    "orchid": "#DA70D6",
    "mediumorchid": "#BA55D3",
    "indigo": "#4B0082",
    "mediumspringgreen": "#00FA9A",
    "tomato": "#FF6347",
    "mediumblue": "#0000CD",
    "midnightblue": "#191970",
    "deepskyblue": "#00BFFF",
    "salmon": "#FA8072",
    "rosybrown": "#BC8F8F",
    "mediumslateblue": "#7B68EE",
    "moccasin": "#FFE4B5",
    "paleturquoise": "#AFEEEE",
    "darkblue": "#00008B",
    "navy": "#000080",
    "steelblue": "#4682B4",
    "crimson": "#DC143C",
    "red": "#FF0000",
    "bisque": "#FFE4C4",
    "darkslategray": "#2F4F4F",
    "maroon": "#800000",
    "mediumpurple": "#9370DB",
    "darkslateblue": "#483D8B",
    "darksalmon": "#E9967A",
    "deeppink": "#FF1493",
    "seagreen": "#2E8B57",
    "mediumvioletred": "#C71585",
    "greenyellow": "#ADFF2F",
    "springgreen": "#00FF7F",
    "sandybrown": "#F4A460",
    "brown": "#A52A2A",
    "lightpink": "#FFB6C1",
    "olive": "#808000",
    "burlywood": "#DEB887",
    "dodgerblue": "#1E90FF",
    "darkolivegreen": "#556B2F",
    "lightsalmon": "#FFA07A",
    "aqua": "#00FFFF",
    "khaki": "#F0E68C",
    "pink": "#FFC0CB",
    "green": "#008000",
    "darkorange": "#FF8C00",
    "rebeccapurple": "#663399",
    "coral": "#FF7F50",
    "darkviolet": "#9400D3",
    "purple": "#800080",
    "palevioletred": "#DB7093",
    "lightseagreen": "#20B2AA",
    "indianred": "#CD5C5C",
    "darkkhaki": "#BDB76B",
    "lightcoral": "#F08080",
    "mediumturquoise": "#48D1CC",
    "peachpuff": "#FFDAB9",
    "skyblue": "#87CEEB",
    "fuchsia": "#FF00FF",
    "navajowhite": "#FFDEAD",
    "lawngreen": "#7CFC00",
    "cornflowerblue": "#6495ED",
    "tan": "#D2B48C",
    "darkred": "#8B0000",
    "firebrick": "#B22222",
    "gold": "#FFD700",
    "yellow": "#FFFF00",
    "wheat": "#F5DEB3",
    "chartreuse": "#7FFF00",
    "goldenrod": "#DAA520",
    "violet": "#EE82EE",
    "yellowgreen": "#9ACD32",
    "cadetblue": "#5F9EA0",
    "plum": "#DDA0DD",
}

NET_COLORS = tuple(tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)) for value in _CSS4_COLORS.values())
BACKGROUND_COLOR = (1.0, 1.0, 1.0, 1.0)
DRILL_COLOR = (0.6, 0.6, 0.6, 1.0)
# Component envelope color sampled from the supplied reference (#b87333).
COMPONENT_OUTLINE_COLOR = (184 / 255, 115 / 255, 51 / 255)
COMPONENT_COLORS = {"top": COMPONENT_OUTLINE_COLOR, "bottom": COMPONENT_OUTLINE_COLOR}
# Reserved interaction colors, outside CSS4_COLORS. The dark keyline makes
# these states distinguishable even over a visually similar network material.
HOVER_COLOR = (0 / 255, 87 / 255, 255 / 255)  # #0057FF
SELECTION_COLOR = (255 / 255, 0 / 255, 110 / 255)  # #FF006E
HIGHLIGHT_KEYLINE_COLOR = (17 / 255, 24 / 255, 39 / 255)  # #111827
# Thin shape outlines share the near-black keyline.
OUTLINE_COLOR = HIGHLIGHT_KEYLINE_COLOR


def net_color(net_id: int) -> tuple[float, ...] | None:
    """Match nets.plot's existing CSS4 palette; id zero retains layer color."""
    return NET_COLORS[(net_id - 1) % len(NET_COLORS)] if net_id else None
