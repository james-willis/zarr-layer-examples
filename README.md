# Zarr-Layer Examples

A collection of interactive web examples demonstrating how to visualize geospatial Zarr datasets using [@carbonplan/zarr-layer](https://github.com/carbonplan/zarr-layer) and MapLibre GL.

## What's Inside

This repository contains several examples showing different ways to work with Zarr data in web applications:

- **Basic Example** - Simple local Zarr dataset visualization
- **Rainy Day Example** - ERA5 weather data with time-series selection
- **Public S3 Example** - Loading Zarr data from public cloud storage
- **Private S3 Example** - Secure access to private S3 buckets *(not currently supported by zarr-layer, see [issue #3](https://github.com/carbonplan/zarr-layer/issues/3))*

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

## TODOs

Future examples we'd like to add:

- [ ] Multi-band visualization (RGB composites)
- [ ] Band Math using custom fragment shaders for derived values
- [ ] Time animation with playback controls
- [ ] Globe projection example
- [ ] Stacking multiple layers with opacity control, composing with Deck.gl

## About Zarr-Layer

[@carbonplan/zarr-layer](https://github.com/carbonplan/zarr-layer) is a JavaScript library for rendering Zarr datasets in MapLibre or Mapbox GL. It supports v2 and v3 Zarr stores, globe and mercator projections, and custom fragment shaders for advanced visualizations.
