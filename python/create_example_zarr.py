import xarray as xr
import numpy as np
from ndpyramid import pyramid_reproject
import rioxarray  # noqa

x = np.arange(-180, 180, 0.25)
y = np.arange(-90, 90.25, 0.25)

tile_resolution = 256 # pixels
tile_dest = f"../app/example_zarrs/example{tile_resolution}.zarr"

da = xr.DataArray(
    data=np.ones((len(y), len(x))),
    coords={"y": y, "x": x},
    dims=["y", "x"],
    name="my_array",
)

da = da * (np.abs(da.y) + np.abs(da.x) + 1)

ds = xr.Dataset({"my_array": da})
ds = ds.rio.write_crs("EPSG:4326")

pyramids = pyramid_reproject(ds, levels=6, resampling="bilinear", pixels_per_tile=tile_resolution)
pyramids.to_zarr(tile_dest, consolidated=True, mode="w", zarr_format=2)
print(f"Result saved to {tile_dest}")