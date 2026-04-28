from pathlib import Path
from typing import cast

import geopandas as gpd
import pandas as pd
import xarray as xr
from shapely.geometry import LineString


def read_points_from_atl08(*, filepath: Path) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame containing points representing ground tracks."""
    gdfs = []
    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        ds = xr.open_dataset(
            filepath, group=f"{ground_track}/land_segments/", chunks={}
        )
        lats = ds.latitude
        lons = ds.longitude

        gdf = gpd.GeoDataFrame(
            data={"ground_track": [ground_track] * len(lons)},
            geometry=gpd.points_from_xy(lons, lats),
            crs="EPSG:4326",
        )

        gdfs.append(gdf)

    combined_gdf = pd.concat(gdfs)
    combined_gdf = cast("gpd.GeoDataFrame", combined_gdf)

    return combined_gdf


def lines_from_atl08_points(*, points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame containing linestrings representing ground tracks.


    GeoDataFrame contains one linestring per ground track from the
    `land_segments` group in the given ATL08 filepath.
    """
    linestrings = {}
    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        linestring = LineString(
            points[points.ground_track == ground_track].geometry.to_list()
        )

        linestrings[ground_track] = linestring

    lines = gpd.GeoDataFrame(
        data={"ground_track": list(linestrings.keys())},
        geometry=list(linestrings.values()),
        crs="EPSG:4326",
    )

    return lines
