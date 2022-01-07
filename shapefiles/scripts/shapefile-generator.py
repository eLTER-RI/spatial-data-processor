import os
import json
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


# helper
def fetchDeimsSiteMetadata(deims_site_id_suffix):
    base_url = 'https://deims.org/api/sites/{}'

    # fetch and parse metadata
    with urllib.request.urlopen(base_url.format(deims_site_id_suffix)) as f:
        full_metadata = json.loads(f.read().decode('utf-8'))

    # take only what we need
    compact_metadata = {
            'id': full_metadata['id'],
            'displayName': full_metadata['attributes']['general']['siteName'],
            'nationalZonesAvailable': False,
            'nationalZoneDir': None,
            }

    return compact_metadata


# helper
def fetchDeimsSiteBoundaries(deims_site_id_suffix):
    # even though IDs are given with a prefix it seems unlikely
    # this prefix will change
    deims_site_id_string = f'https://deims.org/{deims_site_id_suffix}'
    base_url = 'https://deims.org/geoserver/deims/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=deims:deims_sites_boundaries&srsName=EPSG:4326&CQL_FILTER=deimsid=%27{}%27&outputFormat=SHAPE-ZIP'

    # great, you can just pass URLs directly to geopandas
    boundaries = gpd.read_file(base_url.format(deims_site_id_string))

    return boundaries


# complete
def getNewDeimsSite(deims_site_id_suffix,debug=False):
    # TODO: incorporate out-of-repo DEIMS module for validation and fetching functionality
    if deims_site_id_suffix.startswith('https://deims.org/'):
        deims_site_id_suffix = deims_site_id_suffix[18:]
        if debug:
            print('Possible full DEIMS ID detected - trimmed input to {}'.format(deims_site_id_suffix))

    # we probably have a valid DEIMS ID, proceed
    # fetch metadata
    metadata = fetchDeimsSiteMetadata(deims_site_id_suffix)

    # fetch boundaries
    boundaries = fetchDeimsSiteBoundaries(deims_site_id_suffix)

    # create composites
    composites = {}
    for european_zone in [x for x in list(validated_zones) if validated_zones[x]['nat_zone_group'] is None]:
        composite = decomposeSite(
                boundaries,
                validated_zones[european_zone]['boundaries'],
                validated_zones[european_zone]['metadata']['IDColumn'],
                validated_zones[european_zone]['metadata']['nameColumn'],
                debug=False
                )

        # add to composites dictionary
        composites[european_zone] = composite

    return {
            'metadata': metadata,
            'boundaries': boundaries,
            'composites': composites,
            }


def generateMissingComposites(deims_root,validated_deims_sites,validated_zones):
    """Run this to add any missing shapefiles"""
    # possibly add some validate mode where no action is taken
    #
    # accepts two dictionaries, intended to be the output of loadAllInfo
    # doesn't check for correctness and bases results on this
    european_zones = [x for x in list(validated_zones) if validated_zones[x]['nat_zone_group'] is None]

    for site in list(validated_deims_sites):
        # check all european-wides are available
        missing_euros = [x for x in european_zones if x not in validated_deims_sites[site]['composites']]
        # if national zones, check they're all available
        missing_nationals = []
        if validated_deims_sites[site]['metadata']['nationalZonesAvailable']:
            national_zones = [x for x in list(validated_zones) if validated_zones[x]['nat_zone_group']==validated_deims_sites[site]['metadata']['nationalZoneDir']]
            missing_nationals = [x for x in national_zones if x not in validated_deims_sites[site]['composites']]

        # create and save missing composites
        # could later return updated dict(s) instead
        if missing_euros:
            print(f'site {site} is missing european zones {missing_euros}')
            for x in missing_euros:
                composite = decomposeSite(
                    validated_deims_sites[site]['boundaries'],
                    validated_zones[x]['boundaries'],
                    validated_zones[x]['metadata']['IDColumn'],
                    validated_zones[x]['metadata']['nameColumn'],
                    debug=False
                    )
                composite_path = f'{deims_root}/{validated_deims_sites[site]["metadata"]["id"]["suffix"]}/composites/{x}'
                os.makedirs(composite_path,exist_ok=True)
                composite.to_file(f'{composite_path}/boundaries.shp.zip')

        if missing_nationals:
            print(f'site {site} is missing national zones {missing_nationals}')
            for x in missing_nationals:
                composite = decomposeSite(
                    validated_deims_sites[site]['boundaries'],
                    validated_zones[x]['boundaries'],
                    validated_zones[x]['metadata']['IDColumn'],
                    validated_zones[x]['metadata']['nameColumn'],
                    debug=False
                    )
                composite_path = f'{deims_root}/{validated_deims_sites[site]["metadata"]["id"]["suffix"]}/composites/{x}'
                os.makedirs(composite_path,exist_ok=True)
                composite.to_file(f'{composite_path}/boundaries.shp.zip')

    print('done')
