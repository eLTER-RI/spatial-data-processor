# spatial-data-processor
RShiny app providing an interface for templated data workflows to the eLTER community.

## About
This README describes the repo at a high level.
In the documentation folder there is additionally:
- *tutorials* for beginners
- *how-to* guides covering specific topics in detail
- *reference* materials which document the technical details of the system as a whole

This repository contains two primary codebases, along with supporting resources:
- `app.R`, a web-based user interface
- `analyse.py`, which defines workflows the interface can apply to user data.

The interface is written in R using the [shiny framework](https://shiny.rstudio.com/).
The workflows are written in python 3 using third-party libraries, documented with each individual workflow.

## Workflows
Initially, two workflows have been developed.
Both extract data relevant to a chosen [DEIMS site](https://deims.org) from input data.

The first (wf1) works with geospatial raster data.
The user can upload raster data and the data is cropped to the boundaries of the chosen DEIMS site.
The cropped data can be downloaded along with a plot which is displayed as a preview.

The second (wf2) works with "tabular" data (e.g. CSV, spreadsheets, etc.) representing observations associated with spatial regions (e.g. counties, census zones).
The entries corresponding to regions falling within the boundaries of a chosen DEIMS site are filtered, previewed and made available for download, with additional spatial metadata attached.
The following diagram illustrates the filtering process.
![Visual description of workflow 2](documentation/wf2.png)

## Installation
The complete system is provided as a service in UKCEH's [datalabs](https://datalab.datalabs.ceh.ac.uk/) platform, in which it has been developed.
You are welcome to install the system elsewhere using the [installation guide](documentation/howto/install.md) provided.

## Sources
Sample data
- Nitrous oxide data: https://naei.beis.gov.uk/data/map-uk-das
- Scottish birth data: https://statistics.gov.scot/home
- Spain grassland data: https://www.copernicus.eu/

Shapefiles
- DEIMS sites: https://deims.org/
- EU NUTS regions: https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts
- National statistical zone spatial data is cited in each relevant DEIMS directory (e.g. shapefiles/deims/cairngorms for Scottish data)

European Commission NUTS 2016 data © EuroGeographics for the administrative boundaries
