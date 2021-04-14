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


# wf1 shapefiles
# nuts
#base_nuts = gpd.read_file('zip://shapefiles/zones/nuts2016/NUTS_RG_01M_2016_3857.shp.zip')
all_nuts = gpd.read_file('zip://shapefiles/zones/nuts2016/NUTS_RG_01M_2016_3857.shp.zip')
# deims
aa = gpd.read_file('shapefiles/deims/atelier-alpes/raw/boundaries.shp')
bi = gpd.read_file('shapefiles/deims/braila-islands/raw/boundaries.shp')
cg = gpd.read_file('shapefiles/deims/cairngorms/raw/boundaries.shp')
dn = gpd.read_file('shapefiles/deims/donana/raw/boundaries.shp')
ew = gpd.read_file('shapefiles/deims/eisenwurzen/raw/boundaries.shp')
lo = gpd.read_file('shapefiles/deims/lautaret-oisans/raw/boundaries.shp')


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
cg_n0 = gpd.read_file('shapefiles/deims/cairngorms/nuts0/boundaries.shp')
cg_n1 = gpd.read_file('shapefiles/deims/cairngorms/nuts1/boundaries.shp')
cg_n2 = gpd.read_file('shapefiles/deims/cairngorms/nuts2/boundaries.shp')
cg_n3 = gpd.read_file('shapefiles/deims/cairngorms/nuts3/boundaries.shp')
cg_dz = gpd.read_file('shapefiles/deims/cairngorms/scot-data-zones/boundaries.shp')
cg_iz = gpd.read_file('shapefiles/deims/cairngorms/intermediate-zones/boundaries.shp')
cg_hb = gpd.read_file('shapefiles/deims/cairngorms/health-boards/boundaries.shp')
cg_ia = gpd.read_file('shapefiles/deims/cairngorms/integration-authorities/boundaries.shp')
cg_up = gpd.read_file('shapefiles/deims/cairngorms/uk-constituencies/boundaries.shp')
cg_sp = gpd.read_file('shapefiles/deims/cairngorms/scottish-constituencies/boundaries.shp')
cg_sc = gpd.read_file('shapefiles/deims/cairngorms/councils/boundaries.shp')
cg_ew = gpd.read_file('shapefiles/deims/cairngorms/electoral-wards/boundaries.shp')
cg_tw = gpd.read_file('shapefiles/deims/cairngorms/ttw-areas/boundaries.shp')
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
# lautaret-oisans
lo_n0 = gpd.read_file('shapefiles/deims/lautaret-oisans/nuts0/boundaries.shp')
lo_n1 = gpd.read_file('shapefiles/deims/lautaret-oisans/nuts1/boundaries.shp')
lo_n2 = gpd.read_file('shapefiles/deims/lautaret-oisans/nuts2/boundaries.shp')
lo_n3 = gpd.read_file('shapefiles/deims/lautaret-oisans/nuts3/boundaries.shp')

ltser_site_name_dict = {
    'aa': 'LTSER Zone Atelier Alpes',
    'bi': 'Braila Islands',
    'cg': 'Cairngorms National Park',
    'dn': 'Doñana LTSER',
    'ew': 'LTSER Platform Eisenwurzen',
    'lo': 'LTSER platform Lautaret-Oisans',
    }
admin_zones_name_dict = {
    'n0': 'NUTS level 0',
    'n1': 'NUTS level 1',
    'n2': 'NUTS level 2',
    'n3': 'NUTS level 3',
    'dz': 'data zones',
    'iz': 'intermediate zones',
    'hb': 'health boards',
    'ia': 'integration authorities',
    'up': 'UK parliament constituencies',
    'sp': 'Scottish parliament constituencies',
    'sc': 'councils',
    'ew': 'electoral wards',
    'tw': 'travel-to-work areas',
    }

# "gridded" workflow
def cropRasterDataset(dataset,zone_type,region,plot_title):

    active_dataset = rio.open(dataset)
    
    if region == 'aa':
        ltser_site = aa
    elif region == 'bi':
        ltser_site = bi
    elif region == 'cg':
        ltser_site = cg
    elif region == 'dn':
        ltser_site = dn
    elif region == 'ew':
        ltser_site = ew
    else:
        ltser_site = lo
        
    #all_nuts = base_nuts

    global all_nuts
    if ltser_site.crs != active_dataset.crs:
        ltser_site = ltser_site.to_crs(active_dataset.crs)
    if all_nuts.crs != active_dataset.crs:
        all_nuts = all_nuts.to_crs(active_dataset.crs)

    fig, ax = plt.subplots()
    ax.set_axis_off()
    
    if zone_type == 'nuts':
        out_image, out_transform = riomask.mask(active_dataset, all_nuts[all_nuts['NUTS_ID']==region].geometry, crop=True)
        ax.set_title('{} data cropped to NUTS region {}'.format(plot_title,region))
    elif zone_type == 'deims':
        ltser_site_name = ltser_site_name_dict[region]
        out_image, out_transform = riomask.mask(active_dataset, ltser_site.geometry, crop=True)
        ax.set_title('{} data cropped to {}'.format(plot_title,ltser_site_name))
    
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
    fig.savefig('/tmp/crop.png')
    plt.close(fig)
    
    return 0



# "non-gridded" workflow
def aggregateTabularDataset(dataset,ltser_site,admin_zones,plot_key,plot_title):
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
        elif admin_zones == 'iz':
            base_shapefile = cg_iz
        elif admin_zones == 'hb':
            base_shapefile = cg_hb
        elif admin_zones == 'ia':
            base_shapefile = cg_ia
        elif admin_zones == 'up':
            base_shapefile = cg_up
        elif admin_zones == 'sp':
            base_shapefile = cg_sp
        elif admin_zones == 'sc':
            base_shapefile = cg_sc
        elif admin_zones == 'ew':
            base_shapefile = cg_ew
        elif admin_zones == 'tw':
            base_shapefile = cg_tw
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
    elif ltser_site == 'lo':
        if admin_zones == 'n0':
            base_shapefile = lo_n0
        elif admin_zones == 'n1':
            base_shapefile = lo_n1
        elif admin_zones == 'n2':
            base_shapefile = lo_n2
        else:
            base_shapefile = lo_n3
    else:
        base_shapefile = cg_dz
    

    ltser_site_name = ltser_site_name_dict[ltser_site]
    admin_zones_name = admin_zones_name_dict[admin_zones]

    right_on_key = dataset.columns[0]

    # merge
    merged_dataset = pd.merge(base_shapefile,dataset,how='left',left_on='zone_id',right_on=right_on_key)
    
    # plot output
    fig, ax = plt.subplots()
    # from geopandas docs: align legend to plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    # additional formatting
    ax.set_axis_off()
    ax.set_title('{} data cropped to {} by {}'.format(plot_title,ltser_site_name,admin_zones_name))
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
