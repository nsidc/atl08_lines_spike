from pathlib import Path

import geopandas as gpd
import xarray as xr
from shapely.geometry import LineString


def read_geoms_from_atl08(*, filepath: Path) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame containing linestrings representing ground tracks.


    GeoDataFrame contains one linestring per ground track from the
    `land_segments` group in the given ATL08 filepath.
    """
    linestrings = {}
    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        ds = xr.open_dataset(
            filepath, group=f"{ground_track}/land_segments/", chunks={}
        )
        lats = ds.latitude
        lons = ds.longitude

        gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(lons, lats),
            crs="EPSG:4326",
        )

        linestring = LineString(gdf.geometry.to_list())

        linestrings[ground_track] = linestring

    lines = gpd.GeoDataFrame(
        data={"ground_track": list(linestrings.keys())},
        geometry=list(linestrings.values()),
        crs="EPSG:4326",
    )

    return lines


if __name__ == "__main__":
    """Manual test case assuming a `data` dir in the project root with
    `ATL08_20260118035703_05313006_007_01.h5" present. To run:

    uv run python src/atl08_lines/read_geom.py
    """
    this_dir = Path(__file__).parent

    data_dir = this_dir / ".." / ".." / "data"
    lines = read_geoms_from_atl08(
        filepath=data_dir / "ATL08_20260118035703_05313006_007_01.h5"
    )

    lines.to_file(data_dir / "ATL08_20260118035703_05313006_007_01.h5.gpkg")
