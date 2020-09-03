import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# this function expects two GeoDataFrames and two strings and returns a GeoDataFrame
# representing the decomposition of the first GDF by the elements of the second gdf.
# 
# ltser_site - the gdf to decompose
# admin_zones - a gdf of "admin zones" describing the areas to break ltser_site into
# zone_id - the column name of the zone ID in admin_zones
# zone_name - the column name of the zone name in admin_zones

def decomposeSite(ltser_site, admin_zones, zone_id, zone_name, debug=False):
    # convert CRS of dataset to match admin zones
    # this will be the CRS of the output gdf
    ltser_site = ltser_site.to_crs(admin_zones.crs)
    
    # check which zones intersect the LTSER site
    ltser_zones = gpd.overlay(ltser_site,admin_zones,how='intersection')
    
    # add original zones for area comparison, setting correct geometry
    # this is necessary to align the comparison geometry correctly:
    # comparing straight away with admin_zones.geometry.area doesn't
    # align the rows correctly
    ltser_zones = pd.merge(ltser_zones,admin_zones,on=zone_id)
    ltser_zones = ltser_zones.set_geometry('geometry_x')
    
    # add intersection area/zone area as new column
    # full_areas definition necessary because pd.merge only allows for one geoseries
    full_areas = gpd.GeoSeries(ltser_zones['geometry_y'])
    ltser_zones['intersection_ratio'] = ltser_zones.geometry.area/full_areas.area
        
    # construct gdf of cropped zones + ratio of area intersection
    gdf_out = gpd.GeoDataFrame(
        {
            'zone_id': ltser_zones[zone_id].astype("string"),
            'zone_name': ltser_zones[zone_name+'_x'].astype("string"),
            'geometry': ltser_zones['geometry_x'],
            'area_ratio': ltser_zones['intersection_ratio']
        },
        crs = ltser_zones.crs
    )
    
    # optional visual check of intersection adds full geometry of zones
    if debug:
        # add and set full geometry
        gdf_out['debug_geometry'] = ltser_zones['geometry_y']
        gdf_out = gdf_out.set_geometry('debug_geometry')
        
        # plot overlap - no need to return object since plots directly to (presumably) stdout
        fig, ax = plt.subplots(figsize = (10,10))
        ax.set_axis_off()
        ax.set_title('Zones (blue) intersecting LTSER site (red)')
        gdf_out.plot(ax=ax)
        ltser_site.boundary.plot(color='r',ax=ax)
        
        # drop debug_geometry column so output is identical to non-debug
        gdf_out.drop(columns='debug_geometry',inplace=True)
        gdf_out = gdf_out.set_geometry('geometry')
        return gdf_out
    else:
        return gdf_out

# wrapper which was quick at generating Scottish zone shapefiles
# (other than data zone) en masse. Requires manual check for the
# zone name and zone ID parameters for now but still saves time.
#
# zone_shapefile - filename of a shapefile describing zones
# destination - filename to save the output to
# other kwargs are passed to the decomposeSite function

def shapefileGen(zone_shapefile,destination,**kwargs):
    try:
        sf_in = gpd.read_file('zip://'+zone_shapefile)
    except:
        sf_in = gpd.read_file(zone_shapefile)
    sf_out = decomposeSite(admin_zones=sf_in,**kwargs)
    print(sf_out)
    sf_out.to_file(destination)
    
    return 0

ltser_site = gpd.read_file('path/to/shapefile')

shapefileGen('path/to/zones/shapefile','../deims/site/zone/boundaries.shp',ltser_site=ltser_site,zone_id='ID',zone_name='Name',debug=True)
