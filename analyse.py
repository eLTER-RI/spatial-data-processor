"""Workflows to filter data relevant for geographic sites.

Exports:
    - cropRasterDataset for cropping raster data to site boundaries
    - aggregateTabularDataset for filtering rows of tabular data
"""


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
def cropRasterDataset(dataset,region,dataset_title):
    """wf1: raster workflow - extract a subset of a raster dataset.

    dataset: filepath to a raster dataset to open and crop (str)
    region: region to extract from dataset (GeoDataFrame)
    dataset_title: name of data to use in plot title (str)

    Writes output to /tmp/masked.tif and /tmp/crop.png, returns 0.
    """

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
    ax.set_title(f'{dataset_title} data cropped to {site_name}')
    ax.imshow(out_image[0],norm=colors.LogNorm(vmin=1e-2, vmax=200))
    fig.savefig('/tmp/crop.png')
    plt.close(fig)

    return 0


def aggregateTabularDataset(dataset,deims_site,admin_zones,plot_key,plot_title):
    """wf2: tabular workflow - extract rows from a table relating to a
    DEIMS site.

    Requires two dictionaries to be available as free variables,
    validated_deims_sites and validated_zones. These should contain
    data about available DEIMS sites and administrative zones in a
    certain format - see directoryparse.loadAllInfo.

    dataset: tabular dataset to filter (pandas.DataFrame)
    deims_site: DEIMS site to filter data by (str)
    admin_zones: divided by these boundaries (str)
    plot_key: dataset column to plot (str)
    plot_title: name of data to use in plot title (str)

    Writes plot to /tmp/plot.png and returns pandas.DataFrame.
    """

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
