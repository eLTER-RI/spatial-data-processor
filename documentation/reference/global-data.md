# Global data reference
This guide describes how spatial data about DEIMS sites is managed.
It is aimed at developers or power users.

## Overview
Workflows 1 and 2 both rely on spatial data describing DEIMS sites or statistical zones of interest to extract.
They also rely on metadata about these objects (such as what they're called, a codename to identify them, and where they are) in a predictable structure.

This means that instead of working directly with shapefiles/GeoDataFrames, dictionaries of data should first be created (using `shapefiles/scripts/directoryparse.py`) which are then accessed by the workflows.

## Dictionaries
Reference: `loadDirectory` in `shapefiles/scripts/directoryparse.py`

### DEIMS sites
The first is a dictionary of DEIMS sites.
The key of each site is the DEIMS.ID suffix of that site.

Each site is a dictionary of:
- a dictionary of metadata for the site, `'metadata'`, consisting of:
    - the display name of the site to use in menus, plots etc., `displayName`
    - the full DEIMS.ID, `id`
    - whether national statistical zone data is available, `nationalZonesAvailable`
    - if the above is available, how to find them, `nationalZoneDir`
- the boundaries of the site, `'boundaries'`
- a dictionary of all of the "composite" shapefiles available for that site (wf2 only - see the [wf2 reference documentation](./wf2.md)), `'composites'`, consisting of boundaries keyed by code.

### Administrative zones
The second is a dictionary of administrative zones, for wf2 only.
The key of each set of zones is its codename (see below).

Each set of zones is a dictionary of:
- a dictionary of metadata for the zones, `'metadata'`, consisting of:
    - the display name of the set of zones to use in menus, plots etc., `displayName`
    - the name of the column containing the ID of each zone, `IDColumn`
    - the name of the column containing the display name of each zone, `nameColumn`
- the boundaries of the zone, `'boundaries'`
- whether the set of zones is part of a national zone grouping, `'nat_zone_group'`

## Zone codes
DEIMS sites have their IDs (suffixes, to be precise) as a useful codename, whereas the various administrative zones do not have anything similar.
Since they also require codenames, we follow the below scheme to generate them:

- NUTS: nuts{{year}}-{{level}}, e.g. `nuts2016-3` for NUTS 2016 NUTS 3 regions.
- LAU: lau{{year}}, e.g. `lau2020` for LAU 2020 regions.
- NATIONAL: text short name, e.g. `health-boards`.

See `shapefiles/deims/1b94503d-285c-4028-a3db-bc78e31dea07/composites/` for examples of all three types.
