# crop
# this raster dataset (1) to this shapefile boundary (2)

# WF2
# this tabular dataset (1) to this site (2), divided by these boundaries (3) 

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import rasterio as rio
import rasterio.mask as riomask

nox = rio.open('data/agricn2o17.asc')

all_nuts = gpd.read_file('zip://shapefiles/zones/nuts2016/NUTS_RG_01M_2016_3857.shp.zip')
#all_nuts = all_nuts.to_crs(nox.crs)

cg = gpd.read_file('zip://shapefiles/deims/cairngorms/cairngorms_raw.zip')
#cg = cg.to_crs(nox.crs)
cg_dz = gpd.read_file('shapefiles/deims/cairngorms/scot-data-zones/cairngorms-data-zones.shp')
#cg_n0 = gpd.read_file('shapefiles/deims/cairngorms/nuts0/cairngorms-nuts0-zones.shp')
#cg_n1 = gpd.read_file('shapefiles/deims/cairngorms/nuts1/cairngorms-nuts1-zones.shp')
#cg_n2 = gpd.read_file('shapefiles/deims/cairngorms/nuts2/cairngorms-nuts2-zones.shp')
#cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/cairngorms-nuts3-zones.shp')

# "gridded" workflow
def cropRasterDataset(dataset,zone_type,region='cairngorms'):
    global all_nuts
    global cg
    if dataset == 'nox':
        active_dataset = nox
    else:
        active_dataset = rio.open(dataset)

    all_nuts = all_nuts.to_crs(active_dataset.crs)
    cg = cg.to_crs(active_dataset.crs)
    
    fig, ax = plt.subplots()
    ax.set_axis_off()
    
    if zone_type == 'nuts':
        out_image, out_transform = riomask.mask(active_dataset, all_nuts[all_nuts['NUTS_ID']==region].geometry, crop=True)
        ax.set_title('{} dataset cropped to boundaries of NUTS {}.'.format('NOx',region))
    elif zone_type == 'deims':
        out_image, out_transform = riomask.mask(active_dataset, cg.geometry, crop=True)
        ax.set_title('{} dataset cropped to boundaries of {}.'.format('NOx','Cairngorms LTSER'))
    
    out_meta = active_dataset.meta
    out_meta.update({
        'driver': 'GTiff',
        'height': out_image.shape[1],
        'width': out_image.shape[2],
        'transform': out_transform
        })
    
    with rio.open('/tmp/masked.tif', 'w', **out_meta) as dest:
        dest.write(out_image)
        dest.close()

    ax.imshow(out_image[0],norm=colors.LogNorm(vmin=1e-2, vmax=200))
    fig.savefig('/tmp/crop-preview.png')
    plt.close(fig)
    
    return 0
    
# "non-gridded" workflow
def aggregateTabularDataset(dataset,ltser_site='cairngorms',admin_zones='scot-data-zones'):
    # hardcode cairngorms for now, but can eventually accept two pieces of input from
    # shiny (site and subdivision/zones) to select GDF properly
    right_on_key = dataset.columns[0]
    plot_key = dataset.columns[len(dataset.columns)-1]
    merged_dataset = pd.merge(cg_dz,dataset,how='left',left_on='zone_id',right_on=right_on_key)
    
    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.set_title('{} dataset\'s intersection with {} by {}.'.format('Births','Cairngorms LTSER','data zone'))
    merged_dataset.plot(ax=ax,column=plot_key,legend=True)
    fig.savefig('/tmp/preview.png')
    plt.close(fig)
    
    return merged_dataset.drop(columns=[right_on_key,'geometry'])
