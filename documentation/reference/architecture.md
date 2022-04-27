# Technical architecture
This guide describes the high-level view of how the software is written.
It is aimed at developers or power users.

## Overview
As mentioned in the [README](../../README.md), the two key files are `analyse.py` and `app.R`.
The workflows in `analyse.py` can technically be used independently (for DEIMS sites only, for now) but the interface (`app.R`) cannot - it depends on the workflows being available.
[Reticulate](https://rstudio.github.io/reticulate/) is used to call the Python workflows from within the R session.

## Workflows
The workflows are implemented as simple Python functions in `analyse.py`.
The key Python dependency is [Geopandas](https://geopandas.org/en/stable/), which is used to handle vector DEIMS site boundaries.

Before workflows 1 and 2 can be used, one or more global dictionaries of data must be constructed - see [common spatial dictionaries](./global-data.md) for more info.

NOTE: both workflows currently write data to the `/tmp/` directory - see `analyse.py` or the wf1/2 reference documentation for details.

## Interface
The interface isn't a mandatory part of the repository but is provided as it's useful for the target audience.
It's written in [Shiny](https://shiny.rstudio.com/) using a few dependencies - see `app.R` for the explicit dependencies or `packrat/packrat.lock` for the full recursive list.

### Startup
The interface startup process is as follows:
- An R session runs `app.R`
- R libraries are loaded with Packrat (from `packrat/`), including Shiny
- Reticulate is configured to use the virtual environment `reticulate-venv`
- reticulate loads:
    - the workflow definitions (`analyse.py`)
    - code to add new DEIMS sites (`shapefiles/scripts/shapefile-generator.py`)
    - code to save sites and zones to the filesystem, especially the shapefiles directory (see below) (`shapefiles/scripts/directoryparse.py`)
    - interface specific logic (`interface.py`):
        - the `shapefiles/` directory is parsed to load available deims sites and wf2 "admin zones"
        - mappings of nice display names for users to codes/IDs are created (`deims_site_name_mappings` and `deims_site_zone_options`)
        - a new function is added to get a new DEIMS site which updates said mappings on completion

From here Shiny runs normally, calling Python functions and dictionaries when necessary.
The interface is a sidebarLayout with many reactive components.

## Shapefile directory structure
The `shapefile` directory mainly stores information on DEIMS sites and "admin zones" for the workflows to use.
It comes prepopulated with LTSER platform data but can be added to dynamically.

There are three top-level subdirectories, `deims`, `zones` and `scripts`:
- `scripts` contains Python code rather than data
- `deims` contains DEIMS sites, where each site is a subdirectory
- `zones` contains administrative zones, in three (hopefully self-explanatory) subdirectories, `lau`, `national` and `nuts`.

See `shapefiles/scripts/directoryparse.py, loadAllInfo` for details on how these directories are parsed.
