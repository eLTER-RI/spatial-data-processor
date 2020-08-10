# wf1 - crop
# this raster dataset (1) to this shapefile boundary (2)
# wf2 - aggregate
# this tabular dataset (1) to this site (2), divided by these boundaries (3) 

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import rasterio as rio
import rasterio.mask as riomask
from mpl_toolkits.axes_grid1 import make_axes_locatable


# default data for wf1 - not passed through dynamically since no
# native conversion of data types via reticulate
nox = rio.open('data/agricn2o17.asc')

# wf1 shapefiles
# nuts
all_nuts = gpd.read_file('zip://shapefiles/zones/nuts2016/NUTS_RG_01M_2016_3857.shp.zip')
# deims
aa = gpd.read_file('shapefiles/deims/atelier-alpes/raw/boundaries.shp')
bi = gpd.read_file('shapefiles/deims/braila-islands/raw/boundaries.shp')
cg = gpd.read_file('shapefiles/deims/cairngorms/raw/boundaries.shp')
dn = gpd.read_file('shapefiles/deims/donana/raw/boundaries.shp')
ew = gpd.read_file('shapefiles/deims/eisenwurzen/raw/boundaries.shp')

# wf2 shapefiles
# atelier alpes
aa_n0 = gpd.read_file('shapefiles/deims/atelier-alpes/nuts0/boundaries.shp')
aa_n1 = gpd.read_file('shapefiles/deims/atelier-alpes/nuts1/boundaries.shp')
aa_n2 = gpd.read_file('shapefiles/deims/atelier-alpes/nuts2/boundaries.shp')
aa_n3 = gpd.read_file('shapefiles/deims/atelier-alpes/nuts3/boundaries.shp')
# braila islands
bi_n0 = gpd.read_file('shapefiles/deims/braila-islands/nuts0/boundaries.shp')
bi_n1 = gpd.read_file('shapefiles/deims/braila-islands/nuts1/boundaries.shp')
bi_n2 = gpd.read_file('shapefiles/deims/braila-islands/nuts2/boundaries.shp')
bi_n3 = gpd.read_file('shapefiles/deims/braila-islands/nuts3/boundaries.shp')
# cairngorms
cg_dz = gpd.read_file('shapefiles/deims/cairngorms/scot-data-zones/boundaries.shp')
cg_n0 = gpd.read_file('shapefiles/deims/cairngorms/nuts0/boundaries.shp')
cg_n1 = gpd.read_file('shapefiles/deims/cairngorms/nuts1/boundaries.shp')
cg_n2 = gpd.read_file('shapefiles/deims/cairngorms/nuts2/boundaries.shp')
cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/boundaries.shp')
# donana
dn_n0 = gpd.read_file('shapefiles/deims/donana/nuts0/boundaries.shp')
dn_n1 = gpd.read_file('shapefiles/deims/donana/nuts1/boundaries.shp')
dn_n2 = gpd.read_file('shapefiles/deims/donana/nuts2/boundaries.shp')
dn_n3 = gpd.read_file('shapefiles/deims/donana/nuts3/boundaries.shp')
# eisenwurzen
ew_n0 = gpd.read_file('shapefiles/deims/eisenwurzen/nuts0/boundaries.shp')
ew_n1 = gpd.read_file('shapefiles/deims/eisenwurzen/nuts1/boundaries.shp')
ew_n2 = gpd.read_file('shapefiles/deims/eisenwurzen/nuts2/boundaries.shp')
ew_n3 = gpd.read_file('shapefiles/deims/eisenwurzen/nuts3/boundaries.shp')



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
def aggregateTabularDataset(dataset,ltser_site,admin_zones):
    # prepare merge, starting with shapefile data/metadata
    if ltser_site == 'aa':
        if admin_zones == 'n0':
            base_shapefile = aa_n0
        elif admin_zones == 'n1':
            base_shapefile = aa_n1
        elif admin_zones == 'n2':
            base_shapefile = aa_n2
        else:
            base_shapefile = aa_n3
    elif ltser_site == 'bi':
        if admin_zones == 'n0':
            base_shapefile = bi_n0
        elif admin_zones == 'n1':
            base_shapefile = bi_n1
        elif admin_zones == 'n2':
            base_shapefile = bi_n2
        else:
            base_shapefile = bi_n3
    elif ltser_site == 'cg':
        if admin_zones == 'dz':
            base_shapefile = cg_dz
        elif admin_zones == 'n0':
            base_shapefile = cg_n0
        elif admin_zones == 'n1':
            base_shapefile = cg_n1
        elif admin_zones == 'n2':
            base_shapefile = cg_n2
        else:
            base_shapefile = cg_n3
    elif ltser_site == 'dn':
        if admin_zones == 'n0':
            base_shapefile = dn_n0
        elif admin_zones == 'n1':
            base_shapefile = dn_n1
        elif admin_zones == 'n2':
            base_shapefile = dn_n2
        else:
            base_shapefile = dn_n3
    elif ltser_site == 'ew':
        if admin_zones == 'n0':
            base_shapefile = ew_n0
        elif admin_zones == 'n1':
            base_shapefile = ew_n1
        elif admin_zones == 'n2':
            base_shapefile = ew_n2
        else:
            base_shapefile = ew_n3
    else:
        base_shapefile = cg_dz
    
    ltser_site_name_dict = {
        'aa': 'LTSER Zone Atelier Alpes',
        'bi': 'Braila Islands',
        'cg': 'Cairngorms National Park',
        'dn': 'Doñana LTSER',
        'ew': 'LTSER Platform Eisenwurzen',
    }
    ltser_site_name = ltser_site_name_dict[ltser_site]
    admin_zones_name_dict = {
        'n0': 'NUTS level 0',
        'n1': 'NUTS level 1',
        'n2': 'NUTS level 2',
        'n3': 'NUTS level 3',
        'dz': 'Scottish data zones'
    }
    admin_zones_name = admin_zones_name_dict[admin_zones]

    right_on_key = dataset.columns[0]
    plot_key = dataset.columns[len(dataset.columns)-1]
    
    # merge
    merged_dataset = pd.merge(base_shapefile,dataset,how='left',left_on='zone_id',right_on=right_on_key)
    
    # plot output
    fig, ax = plt.subplots()
    # from geopandas docs: align legend to plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    # additional formatting
    ax.set_axis_off()
    ax.set_title('{} data cropped to {} by {}.'.format('Births',ltser_site_name,admin_zones_name))
    # plot output, save to temporary image and close plot to save memory
    merged_dataset.plot(ax=ax,column=plot_key,legend=True,cax=cax,missing_kwds={'color':'lightgrey'})
    fig.savefig('/tmp/preview.png')
    plt.close(fig)
    
    return merged_dataset.drop(columns=[right_on_key,'geometry'])
