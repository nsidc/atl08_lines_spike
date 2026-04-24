from pathlib import Path

from atl08_lines.read_geom import read_geoms_from_atl08

_THIS_DIR = Path(__file__).parent
TEST_DATA_DIR = _THIS_DIR / "data"


def test_read_geoms_from_atl08():
    test_data_path = TEST_DATA_DIR / "test_atl08.h5"

    lines = read_geoms_from_atl08(filepath=test_data_path)

    assert lines is not None
    # One line per expected ground track
    assert len(lines.ground_track) == 6
