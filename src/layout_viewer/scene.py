
"""Immutable layout snapshots, independent of source applications, Qt and graphics APIs. Coordinates are millimeters."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
import math
from typing import Any, Iterable, Iterator, Literal, Sequence

Point = tuple[float, float]
Ring = tuple[Point, ...]
Bounds = tuple[float, float, float, float]


def union_bounds(bounds: Sequence[Bounds]) -> Bounds | None:
    """Return the enclosing rectangle for a sequence of bounds, or None if empty."""
    if not bounds:
        return None
    return (
        min(b[0] for b in bounds),
        min(b[1] for b in bounds),
        max(b[2] for b in bounds),
        max(b[3] for b in bounds),
    )


def clean_ring(points: Iterable[Iterable[float]]) -> Ring:
    """Validate a contour and remove duplicate adjacent/closing vertices."""
    result = []
    for x, y in points:
        point = (float(x), float(y))
        if not all(math.isfinite(v) for v in point):
            raise ValueError("Contour coordinates must be finite.")
        if not result or point != result[-1]:
            result.append(point)
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    if len(set(result)) < 3:
        raise ValueError("A contour requires at least three distinct points.")
    return tuple(result)


@dataclass(frozen=True)
class SceneLayer:
    """Layer name and display-space RGBA color in the range zero to one."""

    name: str = field(metadata={"description": "Layer name."})
    color: tuple[float, float, float, float] = field(
        metadata={"description": "Display-space RGBA color, with each channel between zero and one."}
    )

    def __post_init__(self) -> None:
        color = tuple(float(v) for v in self.color)
        if len(color) != 4 or any(not math.isfinite(v) or not 0 <= v <= 1 for v in color):
            raise ValueError("Layer color must contain four finite values between zero and one.")
        object.__setattr__(self, "color", color)


@dataclass(frozen=True)
class ScenePolygon:
    """One source object's exterior and independent subtractive holes.

    ``exterior`` and ``holes`` are closed implicitly; do not repeat the first
    point at the end. Points use board coordinates in millimeters.
    """

    object_id: int = field(metadata={"description": "Identifier of the source layout object."})
    layer: str = field(metadata={"description": "Physical layer containing this polygon."})
    net: str | None = field(metadata={"description": "Connected net name, or None if the polygon has no net."})
    exterior: Ring = field(metadata={"description": "Exterior contour in board coordinates, in millimeters."})
    holes: tuple[Ring, ...] = field(
        default=(),
        metadata={"description": "Subtractive contours in board coordinates, in millimeters."},
    )
    component: str | None = field(
        default=None,
        metadata={"description": "Owning component reference, or None if the polygon is not a component pin."},
    )
    component_layer: str | None = field(
        default=None,
        metadata={"description": "Owning component's placement layer; defaults to layer when component is set."},
    )
    component_side: str = field(
        default="top",
        metadata={"description": "Board side of the owning component: top or bottom."},
    )
    pin_name: str | None = field(
        default=None,
        metadata={"description": "Pin name or number, if this polygon represents a component pin."},
    )
    category: str = field(
        default="zone",
        metadata={"description": "Polygon category: zone, trace or pad."},
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "exterior", clean_ring(self.exterior))
        object.__setattr__(self, "holes", tuple(clean_ring(ring) for ring in self.holes))
        _validate_pin_owner(self)
        if self.category not in {"zone", "trace", "pad"}:
            raise ValueError("Polygon category must be zone, trace or pad.")
        if self.component is not None and self.category == "zone":
            object.__setattr__(self, "category", "pad")

    @cached_property
    def bounds(self) -> Bounds:
        """Return the axis-aligned bounds of the exterior contour."""
        x, y = zip(*self.exterior)
        return min(x), min(y), max(x), max(y)


def _point(point: Iterable[float]) -> Point:
    """Convert a coordinate pair to finite floating-point values."""
    result = tuple(float(v) for v in point)
    if len(result) != 2 or not all(math.isfinite(v) for v in result):
        raise ValueError("Coordinates must contain two finite values.")
    return result


def _validate_pin_owner(item: Any) -> None:
    """Validate component ownership metadata and default its layer."""
    if item.component is None:
        return
    if not isinstance(item.component, str) or not item.component:
        raise ValueError("A pin requires a component reference.")
    if item.component_side not in {"top", "bottom"}:
        raise ValueError("Pin component side must be top or bottom.")
    if item.component_layer is None:
        object.__setattr__(item, "component_layer", item.layer)


@dataclass(frozen=True)
class SceneTrace:
    """Analytic line or circular arc, with independent start/end caps.

    A nonzero sweep (radians, positive counterclockwise) selects an arc about
    ``center``. Geometry stays analytic at every zoom level.
    """

    object_id: int = field(metadata={"description": "Identifier of the source layout object."})
    layer: str = field(metadata={"description": "Physical layer containing this trace."})
    net: str | None = field(metadata={"description": "Connected net name, or None if the trace has no net."})
    start: Point = field(metadata={"description": "Trace start point in board coordinates, in millimeters."})
    end: Point = field(metadata={"description": "Trace end point in board coordinates, in millimeters."})
    width: float = field(metadata={"description": "Trace width in millimeters."})
    center: Point | None = field(
        default=None,
        metadata={"description": "Arc center in board coordinates; None represents a straight segment."},
    )
    sweep: float = field(
        default=0.0,
        metadata={"description": "Signed arc sweep in radians; positive values are counterclockwise."},
    )
    end_caps: tuple[str, str] = field(
        default=("round", "round"),
        metadata={"description": "Start and end cap styles: round, flat or extended."},
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", _point(self.start))
        object.__setattr__(self, "end", _point(self.end))
        object.__setattr__(self, "end_caps", tuple(self.end_caps))
        if not math.isfinite(self.width) or self.width <= 0:
            raise ValueError("Trace width must be positive and finite.")
        if len(self.end_caps) != 2 or any(cap not in {"round", "flat", "extended"} for cap in self.end_caps):
            raise ValueError("Trace caps must be round, flat or extended.")
        if not math.isfinite(self.sweep) or abs(self.sweep) > math.tau + 1e-10:
            raise ValueError("Arc sweep must be finite and at most one revolution.")
        if self.center is not None:
            object.__setattr__(self, "center", _point(self.center))
            if not self.sweep or math.dist(self.center, self.start) == 0:
                raise ValueError("An arc requires a nonzero radius and sweep.")
            radius = math.dist(self.center, self.start)
            angle = math.atan2(self.start[1] - self.center[1], self.start[0] - self.center[0]) + self.sweep
            expected = (self.center[0] + radius * math.cos(angle), self.center[1] + radius * math.sin(angle))
            tolerance = max(radius * 1e-6, *(math.ulp(v) * 4 for v in (*self.start, *self.end, *self.center)))
            if math.dist(expected, self.end) > tolerance:
                raise ValueError("Arc endpoint does not match its center and sweep.")
        elif self.sweep:
            raise ValueError("An arc sweep requires a center.")

    @cached_property
    def bounds(self) -> Bounds:
        """Return bounds including the stroke width and end-cap extension."""
        radius = self.width / 2
        if self.center is None:
            # Square caps at diagonal angles can extend by sqrt(2) * radius.
            padding = radius * (math.sqrt(2) if "extended" in self.end_caps else 1)
            return (
                min(self.start[0], self.end[0]) - padding,
                min(self.start[1], self.end[1]) - padding,
                max(self.start[0], self.end[0]) + padding,
                max(self.start[1], self.end[1]) + padding,
            )
        arc_radius = math.dist(self.start, self.center)
        start_angle = math.atan2(self.start[1] - self.center[1], self.start[0] - self.center[0])
        direction = 1 if self.sweep > 0 else -1
        points = [self.start, self.end]
        for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
            if ((angle - start_angle) * direction) % math.tau <= abs(self.sweep) + 1e-12:
                points.append(
                    (self.center[0] + arc_radius * math.cos(angle), self.center[1] + arc_radius * math.sin(angle))
                )
        x, y = zip(*points)
        padding = radius * (math.sqrt(2) if "extended" in self.end_caps else 1)
        return min(x) - padding, min(y) - padding, max(x) + padding, max(y) + padding


@dataclass(frozen=True)
class ScenePad:
    """An SDF pad and its optional circular drill, in world coordinates.

    Shapes are circle, rectangle, rounded rectangle (``oval``) and bullet; size is the
    full width/height, rotation is in radians, and drill position is independent
    of the pad's offset/rotation. One record belongs to one physical layer.
    Component pins retain their owner, placement layer/side and pin name so their
    boundaries can be emphasized independently of same-colored copper.
    """

    object_id: int = field(metadata={"description": "Identifier of the source layout object."})
    layer: str = field(metadata={"description": "Physical layer containing this pad."})
    net: str | None = field(metadata={"description": "Connected net name, or None if the pad has no net."})
    center: Point = field(metadata={"description": "Pad center in board coordinates, in millimeters."})
    size: Point = field(metadata={"description": "Full pad width and height in millimeters."})
    shape: str = field(
        default="circle",
        metadata={"description": "Pad shape: circle, rectangle, oval or bullet."},
    )
    rotation: float = field(default=0.0, metadata={"description": "Pad rotation in radians."})
    corner_radius: float = field(
        default=0.0,
        metadata={"description": "Rounded-corner radius in millimeters."},
    )
    hole_radius: float = field(
        default=0.0,
        metadata={"description": "Circular drill radius in millimeters; zero means no drill."},
    )
    hole_center: Point | None = field(
        default=None,
        metadata={"description": "Drill center in board coordinates, in millimeters; defaults to center."},
    )
    component: str | None = field(
        default=None,
        metadata={"description": "Owning component reference, or None for a non-component pad."},
    )
    component_layer: str | None = field(
        default=None,
        metadata={"description": "Owning component's placement layer; defaults to layer when component is set."},
    )
    component_side: str = field(
        default="top",
        metadata={"description": "Board side of the owning component: top or bottom."},
    )
    pin_name: str | None = field(
        default=None,
        metadata={"description": "Pin name or number, if this pad represents a component pin."},
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "center", _point(self.center))
        object.__setattr__(self, "size", _point(self.size))
        object.__setattr__(self, "hole_center", _point(self.center if self.hole_center is None else self.hole_center))
        if self.shape not in {"circle", "rectangle", "oval", "bullet"}:
            raise ValueError("Unsupported SDF pad shape.")
        if min(self.size) <= 0 or not all(
            math.isfinite(v) for v in (self.rotation, self.corner_radius, self.hole_radius)
        ):
            raise ValueError("Pad dimensions must be positive and finite.")
        if not 0 <= self.corner_radius <= min(self.size) / 2 or self.hole_radius < 0:
            raise ValueError("Invalid pad corner or drill radius.")
        if self.shape == "circle" and self.size[0] != self.size[1]:
            raise ValueError("A circular pad requires equal width and height.")
        _validate_pin_owner(self)

    @cached_property
    def bounds(self) -> Bounds:
        """Return bounds covering both the pad body and its drill."""
        c, s = abs(math.cos(self.rotation)), abs(math.sin(self.rotation))
        x, y = self.center
        if self.shape == "circle":
            rx = ry = self.size[0] / 2
        else:
            rx, ry = (c * self.size[0] + s * self.size[1]) / 2, (s * self.size[0] + c * self.size[1]) / 2
        hx, hy = self.hole_center
        r = self.hole_radius
        return min(x - rx, hx - r), min(y - ry, hy - r), max(x + rx, hx + r), max(y + ry, hy + r)


@dataclass(frozen=True)
class SceneJoin:
    """Convex analytic triangle/quad joining SDF trace segments without seams."""

    object_id: int = field(metadata={"description": "Identifier of the source layout object."})
    layer: str = field(metadata={"description": "Physical layer containing this join."})
    net: str | None = field(metadata={"description": "Connected net name, or None if the join has no net."})
    points: tuple[Point, ...] = field(
        metadata={"description": "Three or four convex join vertices in board coordinates, in millimeters."}
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "points", tuple(_point(p) for p in self.points))
        if len(self.points) not in (3, 4):
            raise ValueError("A join requires three or four points.")

    @cached_property
    def bounds(self) -> Bounds:
        """Return the axis-aligned bounds of the join vertices."""
        x, y = zip(*self.points)
        return min(x), min(y), max(x), max(y)


@dataclass(frozen=True)
class SceneComponent:
    """Component bounding box and reference, already in board coordinates.

    Match ``nets.plot``: the envelope is axis-aligned and must not be rotated
    again. Nets describe membership of the whole component, rather than one pin.
    Bounds use millimeters in ``(xmin, ymin, xmax, ymax)`` order.
    """

    object_id: int = field(metadata={"description": "Identifier of the source component."})
    reference: str = field(metadata={"description": "Component reference designator."})
    layer: str = field(metadata={"description": "Physical layer containing the component envelope."})
    nets: tuple[str, ...] = field(metadata={"description": "Net names connected to the component."})
    bounds: Bounds = field(
        metadata={"description": "Axis-aligned component bounds in millimeters: (xmin, ymin, xmax, ymax)."}
    )
    side: str = field(
        default="top",
        metadata={"description": "Board side containing the component: top or bottom."},
    )

    def __post_init__(self) -> None:
        bounds = tuple(float(v) for v in self.bounds)
        if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds):
            raise ValueError("Component bounds must contain four finite values.")
        if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
            raise ValueError("Component bounds must have positive width and height.")
        if self.side not in {"top", "bottom"}:
            raise ValueError("Component side must be top or bottom.")
        if not self.reference:
            raise ValueError("A component requires a reference name.")
        object.__setattr__(self, "bounds", bounds)
        object.__setattr__(self, "nets", tuple(dict.fromkeys(self.nets)))

    def visible_on(
        self,
        visible_layers: Iterable[str],
        mirror: bool = False,
        net: str | None = None,
        both_sides: bool = False,
    ) -> bool:
        """Use the same layer, network and side selection for outlines and names."""
        return (
            self.layer in visible_layers
            and (both_sides or self.side == ("bottom" if mirror else "top"))
            and (net is None or net in self.nets)
        )


@dataclass(frozen=True)
class SceneObjectInfo:
    """Detached source properties shared by all rendered parts of an object.

    Lengths and diameters are millimeters; trace length follows the source
    centerline, including analytic arcs, without adding end-cap extensions.
    """

    object_id: int = field(metadata={"description": "Identifier of the source layout object."})
    kind: Literal["trace", "via", "pad", "zone"] = field(
        metadata={"description": "Selectable object kind: trace, via, pad or zone."}
    )
    net: str | None = field(default=None, metadata={"description": "Connected net name, if any."})
    width: float | None = field(
        default=None,
        metadata={"description": "Object width in millimeters, if applicable."},
    )
    length: float | None = field(
        default=None,
        metadata={"description": "Object centerline length in millimeters, if applicable."},
    )
    drill_diameter: float | None = field(
        default=None,
        metadata={"description": "Drill diameter in millimeters, if applicable."},
    )
    start_layer: str | None = field(default=None, metadata={"description": "Starting layer of a via, if applicable."})
    stop_layer: str | None = field(default=None, metadata={"description": "Ending layer of a via, if applicable."})
    component: str | None = field(
        default=None,
        metadata={"description": "Owning component reference, if applicable."},
    )
    pin_name: str | None = field(default=None, metadata={"description": "Pin name or number, if applicable."})
    name: str | None = field(default=None, metadata={"description": "Source object name, if available."})

    def __post_init__(self) -> None:
        if self.kind not in {"trace", "via", "pad", "zone"}:
            raise ValueError("Unknown selectable object kind.")
        for name in ("width", "length", "drill_diameter"):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError("Object dimensions must be nonnegative and finite.")


@dataclass(frozen=True)
class LayoutScene:
    """Detached snapshot; layer order is top to bottom, matching board stackup order."""

    layers: tuple[SceneLayer, ...] = field(metadata={"description": "Board layers in top-to-bottom stackup order."})
    polygons: tuple[ScenePolygon, ...] = field(metadata={"description": "Polygon geometry in the scene."})
    title: str = field(default="PCB layout", metadata={"description": "Scene or board title."})
    diagnostics: tuple[str, ...] = field(
        default=(),
        metadata={"description": "Non-fatal messages produced while creating the scene."},
    )
    traces: tuple[SceneTrace, ...] = field(default=(), metadata={"description": "Analytic trace geometry."})
    pads: tuple[ScenePad, ...] = field(default=(), metadata={"description": "Pad geometry."})
    joins: tuple[SceneJoin, ...] = field(default=(), metadata={"description": "Join geometry between trace segments."})
    net_names: tuple[str, ...] = field(default=(), metadata={"description": "Net names represented in the scene."})
    components: tuple[SceneComponent, ...] = field(
        default=(),
        metadata={"description": "Component envelopes shown as separate overlays."},
    )
    object_info: tuple[SceneObjectInfo, ...] = field(
        default=(),
        metadata={"description": "Source properties of selectable objects."},
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "layers", tuple(self.layers))
        object.__setattr__(self, "polygons", tuple(self.polygons))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        for name in ("traces", "pads", "joins", "net_names", "components", "object_info"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        names = [layer.name for layer in self.layers]
        if len(names) != len(set(names)):
            raise ValueError("Scene layer names must be unique.")
        if any(item.layer not in names for item in self.geometry):
            raise ValueError("Every object must belong to a scene layer.")
        if any(component.layer not in names for component in self.components):
            raise ValueError("Every component must belong to a scene layer.")

    @property
    def geometry(self) -> Iterator[ScenePolygon | SceneTrace | ScenePad | SceneJoin]:
        """Iterate copper geometry; component envelopes are separate overlays."""
        from itertools import chain

        return chain(self.polygons, self.traces, self.pads, self.joins)

    @cached_property
    def bounds(self) -> Bounds | None:
        """Return bounds of all geometry and component envelopes, or None if empty."""
        bounds = [item.bounds for item in self.geometry]
        bounds.extend(component.bounds for component in self.components)
        return union_bounds(bounds)