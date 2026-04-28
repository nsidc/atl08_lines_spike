from pathlib import Path

from atl08_lines.read_geom import lines_from_atl08_points, read_points_from_atl08

_THIS_DIR = Path(__file__).parent
TEST_DATA_DIR = _THIS_DIR / "data"


def test_read_point_geoms_from_atl08():
    test_data_path = TEST_DATA_DIR / "test_atl08.h5"

    points = read_points_from_atl08(filepath=test_data_path)

    assert points is not None
    # One line per expected ground track
    assert len(set(points.ground_track)) == 6


def test_lines_from_atl08_points():
    test_data_path = TEST_DATA_DIR / "test_atl08.h5"

    points = read_points_from_atl08(filepath=test_data_path)

    lines = lines_from_atl08_points(points=points)

    assert lines is not None
    # One line per expected ground track
    assert len(lines.ground_track) == 6
