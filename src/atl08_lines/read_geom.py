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
