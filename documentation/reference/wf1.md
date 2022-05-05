# Workflow 1 reference
This guide gives an overview of how workflow 1, the raster workflow, works.
It is aimed at anybody who needs to use the workflow, assuming as little prior knowledge as possible.

See also the [tutorial](../tutorials/user-introduction.md) for a practical introduction.

## Overview
Workflow 1 (also wf1, raster workflow) works with geospatial raster data.
It is defined in `analyse.py` as `cropRasterDataset`.

Its primary inputs are:
- a geospatial raster dataset to filter (`dataset`)
- a DEIMS site to extract (`region`)

It also requires:
- a string describing the data, to use in the plot (`dataset_title`)

It returns the part of the data which covers the DEIMS site as a new dataset.

## Technical description
### Dependencies
#### Python modules
[Rasterio](https://rasterio.readthedocs.io/en/stable/) is used to read and write raster data, as well as to crop the data with its "mask" functionality.
Plotting is done with matplotlib.

[Geopandas](https://geopandas.org/en/stable/) is an implicit dependency because of the common spatial dictionaries - see below.

#### Data
Both the boundaries and the display name (for the plot) of the available sites come from the [common spatial dictionaries](./global-data.md).

### Workflow steps
- Load the dataset
- Load the site details (boundaries and name)
- If necessary, reproject the site boundaries to the CRS of the dataset
- Extract the data and write it to `/tmp/masked.tif`
- Plot the data and write the plot to `/tmp/crop.png`

## Notes
Geotiff is the only file format supported and tested, although theoretically anything supported by Rasterio should work.
For now, output will always be in GeoTIFF format.

In the case of multiband rasters, all bands will be included in the output but only the first will be plotted.
