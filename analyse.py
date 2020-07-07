# crop
# this raster dataset (1) to this shapefile boundary (2)

# WF2
# this tabular dataset (1) to this site (2), divided by these boundaries (3) 

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

cg_dz = gpd.read_file('shapefiles/deims/cairngorms/scot-data-zones/cairngorms-data-zones.shp')
#cg_n0 = gpd.read_file('shapefiles/deims/cairngorms/nuts0/cairngorms-nuts0-zones.shp')
#cg_n1 = gpd.read_file('shapefiles/deims/cairngorms/nuts1/cairngorms-nuts1-zones.shp')
#cg_n2 = gpd.read_file('shapefiles/deims/cairngorms/nuts2/cairngorms-nuts2-zones.shp')
#cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/cairngorms-nuts3-zones.shp')

# "gridded" workflow
def cropRasterDataset(dataset,shapefile):
    pass

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
