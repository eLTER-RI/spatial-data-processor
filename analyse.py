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
all_nuts = all_nuts.to_crs(nox.crs)

cg = gpd.read_file('zip://shapefiles/deims/cairngorms/cairngorms_raw.zip')
cg = cg.to_crs(nox.crs)
cg_dz = gpd.read_file('shapefiles/deims/cairngorms/scot-data-zones/cairngorms-data-zones.shp')
#cg_n0 = gpd.read_file('shapefiles/deims/cairngorms/nuts0/cairngorms-nuts0-zones.shp')
#cg_n1 = gpd.read_file('shapefiles/deims/cairngorms/nuts1/cairngorms-nuts1-zones.shp')
#cg_n2 = gpd.read_file('shapefiles/deims/cairngorms/nuts2/cairngorms-nuts2-zones.shp')
#cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/cairngorms-nuts3-zones.shp')

# "gridded" workflow
def cropRasterDataset(type='nuts',region='UKD44'):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    
    if type == 'nuts':
        out_image, out_transform = riomask.mask(nox, all_nuts[all_nuts['NUTS_ID']==region].geometry, crop=True)
        ax.set_title('{} dataset cropped to boundaries of NUTS {}.'.format('NOx',region))
    elif type == 'deims':
        out_image, out_transform = riomask.mask(nox, cg.geometry, crop=True)
        ax.set_title('{} dataset cropped to boundaries of {}.'.format('NOx','Cairngorms LTSER'))
    
    ax.imshow(out_image[0],norm=colors.LogNorm(vmin=1e-2, vmax=200))

    fig.savefig('/tmp/crop-preview.png')
    plt.close(fig)
    
    return 0
    
# "non-gridded" workflow
def aggregateTabularDataset(dataset,ltser_site='cairngorms',admin_zones='scot-data-zones'):
    # hardcode cairngorms for now, but can eventually accept two pieces of input from
    # shiny (site and subdivision/zones) to select GDF properly
    merged_dataset = pd.merge(cg_dz,dataset,how='left',left_on='zone_id',right_on='DataZone')
    
    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.set_title('{} dataset\'s intersection with {} by {}.'.format('Births','Cairngorms LTSER','data zone'))
    merged_dataset.plot(ax=ax,column='2018',legend=True)
    fig.savefig('/tmp/preview.png')
    plt.close(fig)
    
    return 0
