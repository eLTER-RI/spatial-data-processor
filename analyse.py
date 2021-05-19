import os
import json
import rasterio as rio
import rasterio.mask as riomask
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

# SETUP
# load nuts shapefile for wf1
all_nuts = gpd.read_file('zip://shapefiles/zones/nuts2016/NUTS_RG_01M_2016_3857.shp.zip')

# initialise validated zones and directories to attempt to load metadata from
validated_zones = {}
nuts_zones_to_try = ['nuts0','nuts1','nuts2','nuts3']
national_zone_dirs = os.listdir('shapefiles/zones/')
national_zone_dirs.remove('nuts2016')

# try to load metadata for each NUTS level...
for potential_zone in nuts_zones_to_try:
    try:
        # read the metadata file as JSON
        with open('shapefiles/zones/nuts2016/{}/metadata.json'.format(potential_zone)) as f:
            raw_metadata = f.read()
        metadata = json.loads(raw_metadata)
        # check for required keys
        keys = list(metadata)
        if 'displayName' not in keys or 'IDColumn' not in keys or 'nameColumn' not in keys:
            raise Exception
    except:
        print('FATAL: metadata could not be loaded for zone {} - aborting startup'.format(potential_site))
        raise
    # everything succeeded, so add to validated dict
    validated_zones[potential_zone] = metadata

# ...then try to load metadata for each national zone
for national_dir in national_zone_dirs:
    zone_dirs = os.listdir('shapefiles/zones/{}/'.format(national_dir))
    for national_zone in zone_dirs:
        try:
            # read the metadata file as JSON
            with open('shapefiles/zones/{}/{}/metadata.json'.format(national_dir,national_zone)) as f:
                raw_metadata = f.read()
            metadata = json.loads(raw_metadata)
            # check for required keys
            keys = list(metadata)
            # relaxed metadata requirements for now, compared to NUTS - we won't be
            # generating national shapefiles on the fly for a long time, possibly ever
            if 'displayName' not in keys:
                raise Exception
        except:
            print('ERROR: metadata could not be loaded for zone {} - skipping'.format(potential_site))
            continue
        # everything succeeded, so add to validated dict
        validated_zones[national_zone] = metadata

# initialise validated sites and list of directories
# to attempt to load as DEIMS sites
sites_to_try = os.listdir('shapefiles/deims/')
validated_deims_sites = {}

# try to load each directory as a DEIMS site
for potential_site in sites_to_try:
    # metadata
    try:
        # read the metadata file as JSON
        with open('shapefiles/deims/{}/metadata.json'.format(potential_site)) as f:
            raw_metadata = f.read()
        metadata = json.loads(raw_metadata)
        # check for required keys
        keys = list(metadata)
        if 'id' not in keys or 'displayName' not in keys or 'nationalZonesAvailable' not in keys:
            raise Exception
    except:
        print('ERROR: metadata could not be loaded for site {} - skipping'.format(potential_site))
        continue
    # raw shapefile
    try:
        # load shapefile, make no checks
        site_boundaries = gpd.read_file('shapefiles/deims/{}/raw/boundaries.shp'.format(potential_site))
    except:
        print('ERROR: site boundaries could not be loaded for site {} - skipping'.format(potential_site))
        continue
    # guaranteed composites: NUTS0-3
    try:
        # load each shapefile, make no checks
        nuts0 = gpd.read_file('shapefiles/deims/{}/composites/nuts2016/nuts0/boundaries.shp'.format(potential_site))
        nuts1 = gpd.read_file('shapefiles/deims/{}/composites/nuts2016/nuts1/boundaries.shp'.format(potential_site))
        nuts2 = gpd.read_file('shapefiles/deims/{}/composites/nuts2016/nuts2/boundaries.shp'.format(potential_site))
        nuts3 = gpd.read_file('shapefiles/deims/{}/composites/nuts2016/nuts3/boundaries.shp'.format(potential_site))
        # load into dict
        composites = {
                'nuts0': nuts0,
                'nuts1': nuts1,
                'nuts2': nuts2,
                'nuts3': nuts3,
                }
    except:
        print('ERROR: NUTS shapefiles could not be loaded for site {} - skipping'.format(potential_site))
        continue
    # check for national zones, load if needed
    try:
        # load each shapefile, make no checks
        if metadata['nationalZonesAvailable']:
            # read national zone top-level directory - by convention the composites
            # will be in directories of the same name
            composite_dirs = os.listdir('shapefiles/zones/{}/'.format(metadata['nationalZoneDir']))
            for composite_dir in composite_dirs:
                composites[composite_dir] = gpd.read_file('shapefiles/deims/{}/composites/{}/boundaries.shp'.format(potential_site,composite_dir))
    except:
        print('ERROR: national shapefiles could not be loaded for site {} - not all national zones will be present'.format(potential_site))
        # should be safe to proceed
    # everything succeeded, so add site to validated dict
    validated_deims_sites[potential_site] = {
            'metadata': metadata,
            'site_boundaries': site_boundaries,
            'composites': composites,
            }

# construct metadata for interface
deims_site_name_mappings = {
        validated_deims_sites[x]['metadata']['displayName']: x for x in list(validated_deims_sites)
        }
deims_site_zone_options = {
        x: {
            validated_zones[y]['displayName']: y for y in list(validated_deims_sites[x]['composites'])
            } for x in list(validated_deims_sites)
        }



# WORKFLOW DEFINITIONS
# "gridded" workflow
# this raster dataset (1) to this shapefile boundary (2)
def cropRasterDataset(dataset,zone_type,region,plot_data_type):

    # setup
    # load user data
    active_dataset = rio.open(dataset)
    # get site boundary and name from user input
    if zone_type == 'deims':
        site_boundary = validated_deims_sites[region]['site_boundaries']
        site_name = validated_deims_sites[region]['metadata']['displayName']
    elif zone_type == 'nuts':
        site_boundary = all_nuts[all_nuts['NUTS_ID']==region]
        site_name = region

    # coerce site to dataset CRS
    if site_boundary.crs != active_dataset.crs:
        site_boundary = site_boundary.to_crs(active_dataset.crs)

    # figures
    fig, ax = plt.subplots()
    ax.set_axis_off()

    # here we go
    # intersect site and dataset
    out_image, out_transform = riomask.mask(active_dataset, site_boundary.geometry, crop=True)
    out_meta = active_dataset.meta
    out_meta.update({
        'driver': 'GTiff',
        'height': out_image.shape[1],
        'width': out_image.shape[2],
        'transform': out_transform
        })

    # write cropped data to disk
    with rio.open('/tmp/masked.tif', 'w', **out_meta) as dest:
        dest.write(out_image)
        dest.close()

    # populate and save graph
    ax.set_title('{} data cropped to {}'.format(plot_data_type,site_name))
    ax.imshow(out_image[0],norm=colors.LogNorm(vmin=1e-2, vmax=200))
    fig.savefig('/tmp/crop.png')
    plt.close(fig)

    return 0



# "non-gridded" workflow
# this tabular dataset (1) to this site (2) divided by these boundaries (3) 
def aggregateTabularDataset(dataset,deims_site,admin_zones,plot_key,plot_title):
    # select composite deims/zones shapefile data and metadata
    composite_site = validated_deims_sites[deims_site]['composites'][admin_zones]
    site_name = validated_deims_sites[deims_site]['metadata']['displayName']
    admin_zones_name = validated_zones[admin_zones]['displayName']

    # take name of first column of dataset - will pass to merge function assuming it contains IDs
    right_on_key = dataset.columns[0]

    # figures
    fig, ax = plt.subplots()

    # here we go
    # merge
    merged_dataset = pd.merge(composite_site,dataset,how='left',left_on='zone_id',right_on=right_on_key)

    # plot output
    # from geopandas docs: align legend to plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.1)
    # additional formatting
    ax.set_axis_off()
    ax.set_title('{} data cropped to {} by {}'.format(plot_title,site_name,admin_zones_name))
    # plot output, save to temporary image and close plot to save memory
    #
    # The commented statement includes the missing_kwds argument for prettier
    # plot output when there's missing data. At some stage this seems to
    # have fallen foul of a bug in geopandas where supplying "missing_kwds"
    # when there's no missing data causes an error.
    #
    # Instead of checking for missing values, it will be easier to just 
    # remove the missing_kwds argument until the bug is fixed, as there is
    # already a PR raised on GitHub for geopandas which fixes the issue.
    #
    #merged_dataset.plot(ax=ax,column=plot_key,legend=True,cax=cax,missing_kwds={'color':'lightgrey'})
    merged_dataset.plot(ax=ax,column=plot_key,legend=True,cax=cax)
    fig.savefig('/tmp/plot.png')
    plt.close(fig)

    return merged_dataset.drop(columns=[right_on_key,'geometry'])
