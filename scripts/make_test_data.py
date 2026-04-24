from pathlib import Path

import xarray as xr

TEST_DIR = Path(__file__).parent / ".." / "tests"

SOURCE_DATA_PATH = (
    Path(__file__).parent / ".." / "data" / "ATL08_20260118035703_05313006_007_01.h5"
)

if not SOURCE_DATA_PATH.is_file():
    raise RuntimeError("Source data path does not exist.")


if __name__ == "__main__":
    test_data_dir = TEST_DIR / "data"
    test_data_dir.mkdir(exist_ok=True, parents=True)

    for ground_track in ("gt1l", "gt1r", "gt2l", "gt2r", "gt3l", "gt3r"):
        ds = xr.open_dataset(
            SOURCE_DATA_PATH,
            group=f"{ground_track}/land_segments/",
            chunks={},
        )
        lats = ds.latitude
        filtered_lats = xr.concat(
            [
                lats.isel(delta_time=slice(0, 50)),
                lats.isel(delta_time=slice(-50, None)),
            ],
            dim="delta_time",
            coords="minimal",
        )
        lons = ds.longitude
        filtered_lons = xr.concat(
            [
                lons.isel(delta_time=slice(0, 50)),
                lons.isel(delta_time=slice(-50, None)),
            ],
            dim="delta_time",
            coords="minimal",
        )

        test_ds = xr.Dataset(
            {
                "latitude": filtered_lats,
                "longitude": filtered_lons,
            }
        )

        test_ds.to_netcdf(
            test_data_dir / "test_atl08.h5",
            group=f"{ground_track}/land_segments/",
            mode="a",
        )
