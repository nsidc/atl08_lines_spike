from pathlib import Path
from typing import cast

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
from shapely import linestrings
from shapely.geometry import MultiLineString


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


def lines_from_atl08_points(
    *, points: gpd.GeoDataFrame, gap_threshold_meters: int = 500
) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame containing linestrings representing ground tracks.

    GeoDataFrame contains one MultiLineString per ground track from the
    `land_segments` group in the given ATL08 filepath.
    """
    geod = Geod(ellps="WGS84")
    multi_linestrings = {}
    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        points_for_track = points[points.ground_track == ground_track]

        # Distances between consecutive pairs in meters
        _, _, distances = geod.inv(
            lons1=points_for_track.geometry.x[:-1],
            lats1=points_for_track.geometry.y[:-1],
            lons2=points_for_track.geometry.x[1:],
            lats2=points_for_track.geometry.y[1:],
        )

        # Find gaps where distances are gt the threshold
        gaps = np.where(distances > gap_threshold_meters)[0]
        # create groupings of indices for each linestring, split by the gaps
        # found above.
        groups = np.searchsorted(gaps, points_for_track.index)

        # Construct multilinestring
        lines = linestrings(
            points_for_track.geometry.x,
            points_for_track.geometry.y,
            indices=groups,
        )
        multi_line = MultiLineString(lines=list(lines))

        # Track multilinestring per ground track
        multi_linestrings[ground_track] = multi_line

    all_lines = gpd.GeoDataFrame(
        data={"ground_track": list(multi_linestrings.keys())},
        geometry=list(multi_linestrings.values()),
        crs="EPSG:4326",
    )

    return all_lines
