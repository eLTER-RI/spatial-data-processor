# eLTER-geospatial-data-processor
RShiny app providing templated geospatial data analysis workflows to scientists + others in the eLTER community.

### Workflows
- clipping of geospatial data by user-specified boundaries ("gridded data")
- aggregation of tabular data grouped by spatial regions, within the bounds of a DEIMS site ("non-gridded data")

### Technology
RShiny provides the interactive frontend, while Python 3 handles the analysis.
Spatial data (see shapefiles) is precomputed with geopandas for performance, leaving interactive SQL-style joins to pandas.

Developed in NERC-CEH's [datalabs](https://github.com/NERC-CEH/datalab) platform.

### Sources
Data
- Nitrous oxide data: https://naei.beis.gov.uk/data/map-uk-das
- Scottish birth data: https://statistics.gov.scot/home

Shapefiles
- DEIMS sites: https://deims.org/
- EU NUTS regions: https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts
- Scottish data zones: https://data.gov.uk/dataset/ab9f1f20-3b7f-4efa-9bd2-239acf63b540/data-zone-boundaries-2011

European Commission NUTS 2016 data © EuroGeographics for the administrative boundaries
