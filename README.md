# Zarr-GL Examples

A collection of interactive web examples demonstrating how to visualize geospatial Zarr datasets using [zarr-gl](https://github.com/carbonplan/zarr-gl) and MapLibre GL.

A lot of this code is derived from the examples in the [zarr-gl repo](https://github.com/carderne/zarr-gl)

## What's Inside

This repository contains several examples showing different ways to work with Zarr data in web applications:

- **Basic Example** - Simple local Zarr dataset visualization
- **Rainy Day Example** - ERA5 weather data with time-series selection
- **Public S3 Example** - Loading Zarr data from public cloud storage
- **Private S3 Example** - Secure access to private S3 buckets using AWS SDK

## Quick Start

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Running the Examples

Simply run the setup script:
```bash
./setup.sh
```

This will:
1. Set up a Python virtual environment with uv
2. Install all required dependencies
3. Generate example Zarr datasets if they don't exist
4. Start a local file server at [http://localhost:8000](http://localhost:8000)

Then open your browser and navigate to the examples!

## About Zarr-GL

[zarr-gl](https://github.com/carderne/zarr-gl) is a JavaScript library for visualizing large multidimensional geospatial datasets stored in Zarr format directly in the browser using WebGL.