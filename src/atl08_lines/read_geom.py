from pathlib import Path
from typing import cast

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
from shapely import LineString, Point
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

    Each consitutient LineString in the MultiLineString for a ground track
    represents a continuous line of points with valid observations. Gaps greater
    than `gap_threshold_meters` are where linestrings are split, so that no-data
    areas are more obvious.

    TODO/NOTE: currently, single isolated points are represented by a line 0.25m in
    length. We simply project a point 0.25m along the track from the isolated
    point so that it can be represented without needing to mix geometry types
    (which is usually not possible in a single GIS layer). This might be a bit
    misleading, but is probably better than dropping the point or connecting it
    to an adjacent line that might be far away. We should consider different
    distances for these short lines (maybe make it even less than 0.25 m?)

    TODO/NOTE: currently, lines are constructed from the lat/lon pairs from the
    ATL08 data file, but the ground resolution/area of each point is not
    considered (i.e., the footprint size of each spot on the ground is
    ~17m). Maybe we should buffer endpoints of lines to account for the spot
    size? In which case isolated points could be represented as a line 17m in
    length and the isolated point would be the center of that line? This would
    also be misleading, because we would only be representing this in one axis
    (line length - polyons would be necessary to capture the actual "shape" of
    the ground track).
    """
    geod = Geod(ellps="WGS84")
    multi_linestrings = {}
    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        points_for_track = points[points.ground_track == ground_track].copy()

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

        points_for_track["group"] = groups

        lines = []
        for group_idx in set(groups):
            points_for_group = points_for_track[points_for_track.group == group_idx]
            if len(points_for_group) == 1:
                point_idx = int(points_for_group.index[0])
                if point_idx == 0:
                    adjacent_point = points_for_track.iloc[1]
                else:
                    adjacent_point = points_for_track.iloc[point_idx - 1]

                # Find the forward azimuth between the isolated point and it's adjacent point
                fwd_az, _, _ = geod.inv(
                    lons1=points_for_group.geometry.x,
                    lats1=points_for_group.geometry.y,
                    lons2=adjacent_point.geometry.x,
                    lats2=adjacent_point.geometry.y,
                )

                # Use the fwd azimuth to project a point 0.25m away from the
                # isolated point to construct a short line
                new_lon, new_lat, _ = geod.fwd(
                    lons=points_for_group.geometry.x,
                    lats=points_for_group.geometry.y,
                    az=fwd_az,
                    # TODO: consider different sized distance for these tiny
                    # lines.
                    dist=0.25,
                )

                line = LineString(
                    [*points_for_group.geometry.to_list(), Point(new_lon, new_lat)]
                )
            else:
                line = LineString(points_for_group.geometry.to_list())

            lines.append(line)

        multi_line = MultiLineString(lines=list(lines))

        # Track multilinestring per ground track
        multi_linestrings[ground_track] = multi_line

    all_lines = gpd.GeoDataFrame(
        data={"ground_track": list(multi_linestrings.keys())},
        geometry=list(multi_linestrings.values()),
        crs="EPSG:4326",
    )

    return all_lines
