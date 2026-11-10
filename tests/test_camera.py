import pytest

from layout_viewer_core.camera import Camera


@pytest.mark.parametrize("mirror", [False, True])
def test_camera_coordinate_transforms_round_trip(mirror: bool) -> None:
    camera = Camera(center_x=12.5, center_y=-3.0, scale=7.25, width=800, height=600, mirror=mirror)
    world = (15.25, 4.5)
    assert camera.screen_to_world(*camera.world_to_screen(*world)) == pytest.approx(world)


def test_fit_centers_bounds_and_respects_padding() -> None:
    camera = Camera()
    camera.resize(800, 600)
    camera.fit((0, 0, 100, 50), (100, 20, 100, 80))

    assert (camera.center_x, camera.center_y) == pytest.approx((50, 25 - 60 / (2 * camera.scale)))
    assert camera.scale == pytest.approx(0.9 * min(600 / 100, 500 / 50))


def test_zoom_at_keeps_world_point_under_cursor() -> None:
    camera = Camera(center_x=8, center_y=-2, scale=5, width=640, height=480)
    anchor = camera.screen_to_world(125, 360)
    camera.zoom_at(125, 360, 2.5)
    assert camera.screen_to_world(125, 360) == pytest.approx(anchor)
    assert camera.scale == pytest.approx(12.5)


@pytest.mark.parametrize("factor", [0, -1, float("inf"), float("nan")])
def test_zoom_rejects_nonpositive_or_nonfinite_factors(factor: float) -> None:
    with pytest.raises(ValueError, match="positive and finite"):
        Camera().zoom_at(0, 0, factor)


def test_pan_moves_world_in_drag_direction() -> None:
    camera = Camera(scale=4, width=100, height=100)
    before = camera.screen_to_world(50, 50)
    camera.pan(20, -8)
    after = camera.screen_to_world(50, 50)
    assert after == pytest.approx((before[0] - 5, before[1] - 2))
