# Workflow 2 reference
This guide gives an overview of how workflow 2, the tabular workflow, works.
It is aimed at anybody who needs to use the workflow, assuming as little prior knowledge as possible.

See also the [tutorial](../tutorials/user-introduction.md) for a practical introduction.

## Overview
Workflow 2 (also wf2, tabular workflow) works with geospatial statistical/tabular data.
It is defined in `analyse.py` as `aggregateTabularDataset`.

Its primary inputs are:
- a tabular dataset to filter, where the observations correspond to geographical regions (`dataset`)
- a DEIMS site to extract (`deims_site`)
- a description of the regions the data is grouped by, e.g. NUTS 2016 NUTS 2 regions (`admin_zones`)

It also requires:
- a string describing the data, to use in the plot title (`plot_title`)
- the name of a dataset column to colour the plot with (`plot_key`)

It returns rows of the data which correspond to regions which cover the DEIMS site as a new dataset.
The new dataset also includes some metadata columns which describe how much of each region falls within the site boundaries.

## Technical description
### Dependencies
#### Python modules
[Pandas](https://pandas.pydata.org/) is used to read, write and filter the tabular and spatial datasets.
Plotting is done with matplotlib.

[Geopandas](https://geopandas.org/en/stable/) is an implicit dependency because of the common spatial dictionaries - see below.

#### Data
Input data files (of both csv and excel format) must meet all of these requirements:
- the first column of data must contain IDs (e.g. S01006798 for Scottish data zones, AT122 for NUTS regions) which identify the region the row relates to, **with no extra formatting** (e.g. “AT122 - Niederösterreich-Süd” won’t work)
- the first row contains column name information
- begin on the first line, i.e. there are no textual headers or comments.
- CSV: only contain a single table of data, EXCEL: only contain a single table of data per sheet

The "cookie-cutting" operation (i.e. figuring out which zones fall within a site and by how much) need only be done once for each site+zones combination, and so composite sites must be generated before using this workflow.
Code to do this is provided in `shapefiles/scripts/shapefile-generator.py`.

The boundaries and the display name (for the plot) of the available sites and composite sites come from the [common spatial dictionaries](./global-data.md), as well as the display name of the available zones.

### Workflow steps
- Load the composite site boundaries
- Load the site and zone names
- Merge relevant rows of dataset into composite site GeoDataFrame
- Plot a chloropleth map of the composite site + data and write it to `/tmp/plot.png`
- Drop the GIS data (`geometry` column) and return the data

## Notes
Since the composite sites contain all the spatial information required to attach to the processed dataset, a simple left join on the IDs is all that's needed to produce the new dataset.

The workflow works even when there are multiple rows per zone in the composite due to the nature of the join operation.
