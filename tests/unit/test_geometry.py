import pytest

from oil_tracker.domain.geometry import CoordinateTransform, EllipseGeometry, GlassGeometry


def test_coordinate_transform_round_trip_letterbox():
    transform = CoordinateTransform(1920, 1080, 1000, 800)
    display = transform.source_to_display(537.5, 222.0)
    source = transform.display_to_source(*display)
    assert source == pytest.approx((537.5, 222.0))


def test_ellipse_horizontal_extent():
    ellipse = EllipseGeometry(100, 100, 50, 80)
    assert ellipse.horizontal_extent_at(100) == (50, 150)
    assert ellipse.horizontal_extent_at(181) is None


def test_zero_line_px_and_mm():
    geometry = GlassGeometry(EllipseGeometry(100, 100, 50, 80), zero_line_y=120)
    assert geometry.level_px_from_zero(100) == 20
    assert geometry.level_mm_from_zero(100, 0.25) == 5
