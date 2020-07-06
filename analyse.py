# crop
# this raster dataset (1) to this shapefile boundary (2)

# WF2
# this tabular dataset (1) to this site (2), divided by these boundaries (3) 

import pandas as pd
import geopandas as gpd

cg = gpd.read_file('zip://shapefiles/deims/cairngorms/cairngorms_raw.zip')
cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/cairngorms-nuts3-zones.shp')

def analyseDataset(decomposed_site,dataset):
    return pd.merge(decomposed_site,dataset,on='zone_id',how='left')
