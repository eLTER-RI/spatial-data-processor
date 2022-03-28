import os
import json

import rasterio as rio
import rasterio.mask as riomask
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable


# WORKFLOW DEFINITIONS
# "gridded" workflow
# this raster dataset (1) to this shapefile boundary (2)
def cropRasterDataset(dataset,region,plot_data_type):
    # setup
    # load user data
    active_dataset = rio.open(dataset)

    # get site boundary and name from user input
    site_boundary = validated_deims_sites[region]['boundaries']
    site_name = validated_deims_sites[region]['metadata']['displayName']

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
    ax.set_title(f'{plot_data_type} data cropped to {site_name}')
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
    admin_zones_name = validated_zones[admin_zones]['metadata']['displayName']

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
    ax.set_title(f'{plot_title} data cropped to {site_name} by {admin_zones_name}')
    # plot output, save to temporary image and close plot to save memory
    merged_dataset.plot(ax=ax,column=plot_key,legend=True,cax=cax,missing_kwds={'color':'lightgrey'})
    fig.savefig('/tmp/plot.png')
    plt.close(fig)

    if right_on_key != 'zone_id':
        return merged_dataset.drop(columns=[right_on_key,'geometry'])
    else:
        return merged_dataset.drop(columns='geometry')


# FLUXNET/ICOS workflow
# for this site/data (1), take these variables (2)
def filterColumns(dataset,input_variables):
    # shiny multiselects default to empty, so we prevent annoying error messages here
    if not input_variables:
        return 1
    
    # shiny multiselects are passed as a string when one choice is made, list otherwise
    if type(input_variables) == str:
        input_variables = [input_variables]

    # add _QC columns to output dataframe
    output_variables = input_variables.copy()
    for x in input_variables:
        output_variables.append(x+"_QC")

    # create datetime column for proper plotting
    dataset['PARSED_TIME'] = pd.to_datetime(dataset['TIME'])
    
    # plot
    fig, ax = plt.subplots()
    ax.set_title(f'FLUXNET/ICOS data')
    for x in input_variables:
        ax.plot(dataset['PARSED_TIME'],dataset[x])
    fig.savefig('/tmp/wf3.png')
    plt.close(fig)
    
    # keep just TIME and our chosen variables, along with their _QC observations
    filtered_dataset = dataset.filter(['TIME']+output_variables)

    return filtered_dataset


# write metadata for filterColumns
def writeFilterColumnsMetadata(data_source,site_code,deims_id,variables,output_filename):
    # prep
    if data_source == 'fluxnet':
        dataset = 'FLUXNET2015'
        with open('input/fluxnet/acknowledgement.txt') as f:
            acknowledgement = f.read()
    elif data_source == 'icos':
        dataset = 'ICOS Drought2018'
        with open('input/icos/acknowledgement.txt') as f:
            acknowledgement = f.read()
    
    # here we go
    with open('/tmp/METADATA.txt','w') as f:
        f.write(f'''METADATA
Workflow version: 0.1
Workflow source: https://github.com/eLTER-RI/spatial-data-processor
Source dataset: {dataset}
Selected site: {site_code}, {deims_id}
Selected variables: {variables}
Output filename: {output_filename}

ACKNOWLEDGEMENTS
{acknowledgement}''')
