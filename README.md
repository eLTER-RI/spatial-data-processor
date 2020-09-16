# spatial-data-processor
RShiny app providing templated geospatial data analysis workflows to the eLTER community.

## About
### Workflows
- clipping of geospatial raster data by user-specified boundaries ("gridded data", workflow 1)
- aggregation of tabular data grouped by spatial regions, within the bounds of a DEIMS site ("non-gridded data", workflow 2)

### Architecture
RShiny provides the interactive frontend, while Python 3 handles the analysis.
Spatial data (see shapefiles) is precomputed with geopandas for performance, leaving interactive SQL-style joins to pandas.

Developed in UKCEH's [datalabs](https://github.com/NERC-CEH/datalab) platform.

## Installation
### Prerequisites
- R >=3.5.3
- Python 3 >=3.5.3
- a compatible libpython shared library (installing python3-dev on Linux distributions should ensure this; see [this issue](https://github.com/rstudio/reticulate/issues/637))
- pip/python3 venv module

These dependencies are all provided in the standard datalabs RStudio environment. Python and R versions other than 3.5.3 remain untested, although more recent versions are likely to work

### Setup
- Clone the repo
- Source `setup.R` in an R session to restore the packrat environment
- Create a virtual environment called `reticulate-venv` in the root directory
- Install python dependencies from requirements.txt, with `source reticulate-venv/bin/activate && pip install -r requirements.txt` on Linux

For Linux platforms (and possibly others supporting Bash), `setup.sh` is provided to automate the steps after cloning. Simply run `./setup.sh` in a terminal.

## Sources
Data
- Nitrous oxide data: https://naei.beis.gov.uk/data/map-uk-das
- Scottish birth data: https://statistics.gov.scot/home

Shapefiles
- DEIMS sites: https://deims.org/
- EU NUTS regions: https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts
- National statistical zone spatial data is cited in each relevant DEIMS directory (e.g. shapefiles/deims/cairngorms for Scottish data)

European Commission NUTS 2016 data © EuroGeographics for the administrative boundaries