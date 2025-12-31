import xarray as xr
import numpy as np
from ndpyramid import pyramid_reproject
import rioxarray  # noqa
from zarr.codecs import BytesCodec, GzipCodec, ShardingCodec, BloscCodec
import zarr
from pathlib import Path


def patch_zstd_to_blosc(zarr_path):
    """
    Patch zarr.json files to replace zstd codec with blosc codec.
    Also rewrite the shard data with the new codec.
    This is needed for compatibility with zarr.js which doesn't support standalone zstd.
    """
    zarr_path = Path(zarr_path)
    zarr_store = zarr.open_group(zarr_path, mode="r+", zarr_format=3)

    def process_group(group, path=""):
        for key in list(group.array_keys()):
            arr = group[key]
            full_path = f"{path}/{key}" if path else key

            # Check if it uses sharding with zstd
            if hasattr(arr, 'metadata') and hasattr(arr.metadata, 'codecs'):
                codecs = arr.metadata.codecs
                needs_patch = False
                for codec in codecs:
                    if hasattr(codec, 'configuration') and hasattr(codec.configuration, 'codecs'):
                        for inner_codec in codec.configuration.codecs:
                            if hasattr(inner_codec, 'name') and inner_codec.name == 'zstd':
                                needs_patch = True
                                break

                if needs_patch:
                    # Read the data
                    data = arr[:]
                    shape = arr.shape
                    dtype = arr.dtype
                    chunks = arr.chunks
                    fill_value = arr.fill_value if hasattr(arr, 'fill_value') else None
                    attrs = dict(arr.attrs) if hasattr(arr, 'attrs') else {}
                    dim_names = arr.metadata.dimension_names if hasattr(arr.metadata, 'dimension_names') else None

                    # Calculate shard shape (outer chunks)
                    shard_shape = chunks
                    # Inner chunks should be 1/16 or 1/256 of shard
                    if len(chunks) == 2:
                        inner_chunk_shape = (max(1, chunks[0] // 16), max(1, chunks[1] // 16))
                    elif len(chunks) == 1:
                        inner_chunk_shape = (max(1, chunks[0] // 256),)
                    else:
                        inner_chunk_shape = chunks

                    # Delete old array
                    del group[key]

                    # Create new array with blosc codec
                    new_arr = zarr.create(
                        shape=shape,
                        chunks=shard_shape,
                        dtype=dtype,
                        fill_value=fill_value,
                        store=group.store,
                        path=f"{path}/{key}" if path else key,
                        zarr_format=3,
                        attributes=attrs,
                        dimension_names=dim_names,
                        codecs=[
                            ShardingCodec(
                                chunk_shape=inner_chunk_shape,
                                codecs=[BytesCodec(), BloscCodec(cname='zstd', clevel=5)]
                            )
                        ]
                    )

                    # Write data
                    new_arr[:] = data
                    print(f"  ✓ Recompressed {full_path}: zstd → blosc")

        # Recursively process subgroups
        for key in list(group.group_keys()):
            subgroup = group[key]
            process_group(subgroup, f"{path}/{key}" if path else key)

    process_group(zarr_store)


x = np.arange(-180, 180, 0.25)
y = np.arange(-90, 90.25, 0.25)

tile_resolution = 128  # pixels
tile_dest = f"../app/example_zarrs/example{tile_resolution}v3.zarr"
original_data_dest = f"../app/example_zarrs/original_data{tile_resolution}.zarr"
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

# Clear encodings set by pyramid_reproject (which include v2-style compressor incompatible with Zarr v3)
for node in pyramids.subtree:
    for var_name in list(node.data_vars) + list(node.coords):
        node[var_name].encoding = {}

# Configure encoding with sharding for pyramid levels
print("Writing pyramid with sharding...")
encoding = {}
for node in pyramids.subtree:
    node_encoding = {}

    for var_name in list(node.data_vars) + list(node.coords):
        var = node[var_name]
        # Determine chunk shape
        if hasattr(var, 'chunks') and var.chunks:
            chunk_shape = tuple(c[0] if isinstance(c, tuple) else c for c in var.chunks)
        else:
            chunk_shape = var.shape

        # Skip scalar or empty arrays
        if chunk_shape == () or len(chunk_shape) == 0:
            continue

        ndim = len(chunk_shape)

        # Define shard shape based on dimensionality
        if ndim == 2 and chunk_shape[0] > 0 and chunk_shape[1] > 0:
            # 16x16 inner chunks per shard for 2D arrays
            shard_shape = (chunk_shape[0] * 16, chunk_shape[1] * 16)
        elif ndim == 1 and chunk_shape[0] > 0:
            # 256 inner chunks per shard for 1D arrays
            shard_shape = (chunk_shape[0] * 256,)
        else:
            # For other cases, no sharding
            node_encoding[var_name] = {
                "chunks": chunk_shape,
            }
            continue

        node_encoding[var_name] = {
            "chunks": chunk_shape,  # Internal Zarr array chunk size
            "shards": shard_shape,  # Physical file shard size
        }

    if node_encoding:
        encoding[node.path] = node_encoding


# Write to zarr with sharding
pyramids.to_zarr(tile_dest, consolidated=False, mode="w", zarr_format=3, encoding=encoding, compute=True)
print(f"✓ Pyramid result saved to {tile_dest}")

# Patch zstd codec to blosc for JavaScript compatibility
print("\nPatching codecs for zarr.js compatibility...")
patch_zstd_to_blosc(tile_dest)

# Write original dataset with sharding
print("\nWriting original dataset with sharding...")
ds_encoding = {}
for var_name in list(ds.data_vars) + list(ds.coords):
    var = ds[var_name]
    # Determine chunk shape
    if hasattr(var, 'chunks') and var.chunks:
        chunk_shape = tuple(c[0] if isinstance(c, tuple) else c for c in var.chunks)
    else:
        # Default chunking strategy
        shape = var.shape
        if len(shape) == 2:
            chunk_shape = (min(256, shape[0]), min(256, shape[1]))
        elif len(shape) == 1:
            chunk_shape = (min(1024, shape[0]),)
        else:
            chunk_shape = shape

    # Skip scalar or empty arrays
    if chunk_shape == () or len(chunk_shape) == 0:
        ds_encoding[var_name] = {
            "chunks": chunk_shape,
        }
        continue

    ndim = len(chunk_shape)

    # Define shard shape for original dataset
    if ndim == 2 and chunk_shape[0] > 0 and chunk_shape[1] > 0:
        # 4x4 inner chunks per shard for 2D arrays
        shard_shape = (chunk_shape[0] * 4, chunk_shape[1] * 4)
    elif ndim == 1 and chunk_shape[0] > 0:
        # 16 inner chunks per shard for 1D arrays
        shard_shape = (chunk_shape[0] * 16,)
    else:
        ds_encoding[var_name] = {
            "chunks": chunk_shape,
        }
        continue

    ds_encoding[var_name] = {
        "chunks": chunk_shape,  # Internal Zarr array chunk size
        "shards": shard_shape,  # Physical file shard size
    }


ds.to_zarr(original_data_dest, consolidated=False, mode="w", zarr_format=3, encoding=ds_encoding, compute=True)
print(f"✓ Original dataset saved to {original_data_dest}")

# Patch codecs for JavaScript compatibility
patch_zstd_to_blosc(original_data_dest)

print("\n✅ Done! Note: Consolidated metadata is not used for Zarr v3 (not officially part of the spec)")
