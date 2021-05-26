# Technical architecture
The high-level architecture is as follows:
- app.R sources analyse.py on shiny startup
	- python interprets the directory structure of zones (shapefiles/zones) and deims sites (shapefiles/deims) and creates dictionaries of metadata and spatial data
	- python also defines the two functions which carry out the worrkflows
- everything else is done in R, calling the two data analysis functions and referencing the constructed metadata about which zones are available with which sites etc.

The metadata R reads is:
	- (wf1 + wf2) what sites there are (IDs) and how should they be displayed (friendly name) = `deims_site_name_mappings`
	- (wf2) for each site, which zones are available and how should they be displayed (DICT (lookup by site id) of DICTS (zone friendly name > code mapping)) = `deims_site_zone_options`

At a minimum we can assume each site has:
	- a shapefile describing its boundaries (raw directory)
	- composites with nuts0-3 (since we restrict ourselves to European sites)
