import os
import json
import string
import urllib.request
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# this function expects two GeoDataFrames and two strings and returns a GeoDataFrame
# representing the decomposition of the first GDF by the elements of the second gdf.
# 
# ltser_site - the gdf to decompose
# admin_zones - a gdf of "admin zones" describing the areas to break ltser_site into
# zone_id - the column name of the zone ID in admin_zones
# zone_name - the column name of the zone name in admin_zones

def decomposeSite(ltser_site, admin_zones, zone_id, zone_name, debug=False):

    # convert CRS of dataset to match admin zones
    # this will be the CRS of the output gdf
    ltser_site = ltser_site.to_crs(admin_zones.crs)

    # check which zones intersect the LTSER site
    ltser_zones = gpd.overlay(ltser_site,admin_zones,how='intersection')

    # add original zones for area comparison, setting correct geometry
    # this is necessary to align the comparison geometry correctly:
    # comparing straight away with admin_zones.geometry.area doesn't
    # align the rows correctly
    ltser_zones = pd.merge(ltser_zones,admin_zones,on=zone_id)
    ltser_zones = ltser_zones.set_geometry('geometry_x')

    # add intersection area/zone area as new column
    # full_areas definition necessary because pd.merge only allows for one geoseries
    full_areas = gpd.GeoSeries(ltser_zones['geometry_y'])
    ltser_zones['intersection_ratio'] = ltser_zones.geometry.area/full_areas.area

    # construct gdf of cropped zones + ratio of area intersection
    gdf_out = gpd.GeoDataFrame(
        {
            'zone_id': ltser_zones[zone_id].astype('string'),
            'zone_name': ltser_zones[zone_name+'_x'].astype('string'),
            'geometry': ltser_zones['geometry_x'],
            'area_ratio': ltser_zones['intersection_ratio']
        },
        crs = ltser_zones.crs
    )

    # optional visual check of intersection adds full geometry of zones
    if debug:
        # add and set full geometry
        gdf_out['debug_geometry'] = ltser_zones['geometry_y']
        gdf_out = gdf_out.set_geometry('debug_geometry')

        # plot overlap - no need to return object since plots directly to (presumably) stdout
        fig, ax = plt.subplots(figsize = (10,10))
        ax.set_axis_off()
        ax.set_title('Zones (blue) intersecting LTSER site (red)')
        gdf_out.plot(ax=ax)
        ltser_site.boundary.plot(color='r',ax=ax)

        # drop debug_geometry column so output is identical to non-debug
        gdf_out.drop(columns='debug_geometry',inplace=True)
        gdf_out = gdf_out.set_geometry('geometry')
        return gdf_out
    else:
        return gdf_out

# load NUTS zones 0-3, as these are the only mandatory zones
nuts_zones = {}
nuts_names = ['nuts0', 'nuts1', 'nuts2', 'nuts3']

# try to load each directory as a NUTS zone
for nuts_level in nuts_names:
    # metadata
    try:
        # read the metadata file as JSON
        with open('shapefiles/zones/nuts2016/{}/metadata.json'.format(nuts_level)) as f:
            raw_metadata = f.read()
        metadata = json.loads(raw_metadata)
        # check for required keys
        keys = list(metadata)
        if 'displayName' not in keys or 'IDColumn' not in keys or 'nameColumn' not in keys:
            raise Exception
    except:
        print('FATAL: metadata could not be loaded for zone {} - aborting'.format(nuts_level))
        raise
    # raw shapefile
    try:
        # load shapefile, make no checks
        zone_boundaries = gpd.read_file('zip://shapefiles/zones/nuts2016/{}/boundaries.shp.zip'.format(nuts_level))
    except:
        print('FATAL: zone boundaries could not be loaded for zone {} - skipping'.format(potential_zone))
        raise
    # everything succeeded, so add zone to validated dict
    nuts_zones[nuts_level] = {
            'metadata': metadata,
            'zone_boundaries': zone_boundaries,
            }

# DEIMS interface code
#
# returns True if a string is a well formed DEIMS ID suffix
# no checks are made of whether it is "real"
def isValidDeimsIDSuffix(deims_site_id_suffix,debug=False):
    # check type
    if type(deims_site_id_suffix) != str:
        if debug:
            print('Type should be string')
        return False

    # check length
    if len(deims_site_id_suffix) != 36:
        if debug:
            print('Incorrect length')
        return False

    # check for expected dashes
    split_id_suffix = deims_site_id_suffix.split('-')
    if [len(x) for x in split_id_suffix] != [8, 4, 4, 4, 12]:
        if debug:
            print('Incorrect shape')
        return False

    # check hex characters only - nested "all"s because .split() returns list
    if not all(
            all(
                char in string.hexdigits for char in substring
                ) for substring in split_id_suffix
            ):
        if debug:
            print('Hex characters only')
        return False

    # everything's ok
    return True

# makes no checks, blindly creates the relevant directories needed
# for a new DEIMS site
def bootstrapDeimsDirectory(deims_site_id_suffix):
    # make minimal directories, to be populated with shapefiles and metadata elsewhere
    os.makedirs('shapefiles/deims/{}/raw/'.format(deims_site_id_suffix),exist_ok=True)
    # makedirs creates intermediate directories, so we set up the minimal
    # guaranateed composite directories directly
    os.makedirs('shapefiles/deims/{}/composites/nuts2016/nuts0'.format(deims_site_id_suffix),exist_ok=True)
    os.makedirs('shapefiles/deims/{}/composites/nuts2016/nuts1'.format(deims_site_id_suffix),exist_ok=True)
    os.makedirs('shapefiles/deims/{}/composites/nuts2016/nuts2'.format(deims_site_id_suffix),exist_ok=True)
    os.makedirs('shapefiles/deims/{}/composites/nuts2016/nuts3'.format(deims_site_id_suffix),exist_ok=True)

    return 0

def fetchDeimsSiteMetadata(deims_site_id_suffix,debug=False):
    base_url = 'https://deims.org/api/sites/{}'

    # fetch and parse metadata
    with urllib.request.urlopen(base_url.format(deims_site_id_suffix)) as f:
        full_metadata = json.loads(f.read().decode('utf-8'))

    if debug:
        print(full_metadata)

    # take only what we need
    compact_metadata = {
            'id': full_metadata['id'],
            'displayName': full_metadata['siteName'],
            'nationalZonesAvailable': False,
            'nationalZoneDir': None,
            }

    return compact_metadata

def fetchDeimsSiteBoundaries(deims_site_id_suffix):
    # even though IDs are given with a prefix it seems unlikely
    # this prefix will change
    deims_site_id_string = 'https://deims.org/'+ deims_site_id_suffix
    base_url = 'https://deims.org/geoserver/deims/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=deims:deims_sites_boundaries&srsName=EPSG:4326&CQL_FILTER=deimsid=%27{}%27&outputFormat=SHAPE-ZIP'
    zip_destination = 'shapefiles/deims/{}/raw/boundaries.shp.zip'.format(deims_site_id_suffix)

    # fetch shapefile as zip
    urllib.request.urlretrieve(
            base_url.format(deims_site_id_string),
            zip_destination
            )

    return zip_destination


# putting the above together
# test case: trnava - https://deims.org/fabf28c6-8fa1-4a81-aaed-ab985cbc4906
def addDeimsSite(deims_site_id_suffix,debug=False):
    # check input is valid, trimming full IDs
    #
    # this architecture should probably be integrated
    # with the ID validation checks though, perhaps
    # a unified isDeimsID which returns a normalised
    # form, either full or suffix-only
    if deims_site_id_suffix.startswith('https://deims.org/'):
        deims_site_id_suffix = deims_site_id_suffix[18:]
        if debug:
            print('Possible full DEIMS ID detected - trimmed input to {}'.format(deims_site_id_suffix))
    if not isValidDeimsIDSuffix(deims_site_id_suffix,debug=debug):
        print('Invalid ID')
        return 1

    base_dir = 'shapefiles/deims/{}'.format(deims_site_id_suffix)
    metadata_destination = '{}/{}'.format(base_dir,'metadata.json')

    bootstrapDeimsDirectory(deims_site_id_suffix)
    # fetch and save metadata
    metadata = fetchDeimsSiteMetadata(deims_site_id_suffix,debug=debug)
    with open(metadata_destination,'w') as f:
        f.write(json.dumps(metadata,indent=4))

    # fetch and save raw boundaries, saving the returned path to be read next
    boundaryPath = fetchDeimsSiteBoundaries(deims_site_id_suffix)
    # read boundaries then aggregate with NUTS and save
    deims_site_boundaries = gpd.read_file(boundaryPath)
    for x in list(nuts_zones):
        composite = decomposeSite(
                deims_site_boundaries,
                nuts_zones[x]['zone_boundaries'],
                nuts_zones[x]['metadata']['IDColumn'],
                nuts_zones[x]['metadata']['nameColumn'],
                debug=False
                )
        composite.to_file('{}/composites/nuts2016/{}/boundaries.shp'.format(base_dir,x))
