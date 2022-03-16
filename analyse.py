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
# for this site (1), take these variables (2)
# actually, it's possible that the dataset and site are one and the same here.
def filterColumns(dataset,deims_site,variables):
    # shiny multiselects default to empty, so we prevent annoying error messages here
    if not variables:
        return 1
    
    # shiny multiselects are passed as a string when one choice is made, list otherwise
    if type(variables) == str:
        variables = [variables]
    
    # metadata
    site_name = validated_deims_sites[deims_site]['metadata']['displayName']
    
    # add any _QC columns to output dataframe
    output_variables = variables.copy()
    # using indexes instead of `for x in output_variables` is convenient when .inserting,
    # but requires working right-to-left to preserve indexes after insertions
    for x in range(len(output_variables)-1,-1,-1):
        QC_name = output_variables[x]+"_QC"
        if QC_name in dataset.columns:
            output_variables.insert(x+1,QC_name)

    # keep just TIMESTAMP and our chosen variables
    filtered_dataset = dataset.filter(['TIMESTAMP']+output_variables)
    
    # plot
    fig, ax = plt.subplots()
    ax.set_title(f'FLUXNET/ICOS data')
    for x in variables:
        ax.plot(filtered_dataset['TIMESTAMP'],filtered_dataset[x])
    fig.savefig('/tmp/wf3.png')
    plt.close(fig)

    return filtered_dataset
