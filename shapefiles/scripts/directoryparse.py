import os
import json

import geopandas as gpd


# helper
def bootstrapDeimsDirectory(deims_site_id_suffix,deims_dir):
    ### TODO: test existence of deims_dir, throw error
    ### TODO: test deims suffix for validity

    # OK, proceed
    # makedirs creates intermediate directories, so we need just one call
    os.makedirs(f'{deims_dir}/{deims_site_id_suffix}/composites',exist_ok=True)

    return f'{deims_dir}/{deims_site_id_suffix}'


# utility
def saveDeimsSite(deims_site,base_dir):
    # do we need base dir to exist? Probably not
    target_dir = bootstrapDeimsDirectory(deims_site['metadata']['id']['suffix'],base_dir)

    # metadata
    with open(f'{target_dir}/metadata.json','w') as f:
        f.write(json.dumps(deims_site['metadata'],indent=4))

    # boundaries
    deims_site['boundaries'].to_file(f'{target_dir}/boundaries.shp.zip')

    # composites
    for x in list(deims_site['composites']):
        os.makedirs(f'{target_dir}/composites/{x}',exist_ok=True)
        deims_site['composites'][x].to_file(f'{target_dir}/composites/{x}/boundaries.shp.zip')


# utility
def loadDirectory(directory,dir_type,required_metadata,boundaries_required,nat_zone_group=None):
    """Load a directory as a DEIMS site or zone"""
    # directory: str but whatever os.path.normpath takes really
    # dir_type: 'deims', 'nat-zone', 'eu-zone'
    # required_metadata: list strs
    # boundaries_required: bool
    #
    # PREP
    if dir_type not in ['deims','nat-zone','eu-zone']:
        print('Invalid dir_type')
        raise Exception
    if dir_type == 'nat-zone' and nat_zone_group is None:
        print('nat_zone_group required for nat-zone')
        raise Exception
    directory = os.path.normpath(directory)
    shapefile_path = 'zip://'+directory+'/boundaries.shp.zip'

    # common to DEIMS and ZONES
    # METADATA
    with open(directory+'/metadata.json') as f:
        raw_metadata = f.read()
    metadata = json.loads(raw_metadata)

    # check for required keys
    keys = list(metadata)
    if not all([x in keys for x in required_metadata]):
        print('Metadata missing required attributes')
        raise Exception

    # SHAPEFILE
    try:
        # load shapefile, make no checks
        boundaries = gpd.read_file(shapefile_path)
    except:
        if boundaries_required:
            print(f'FATAL: boundaries could not be loaded for zone {directory} - aborting')
            raise
        else:
            print(f'INFO: boundaries could not be loaded for zone {directory} - continuing')
            boundaries = None

    # DEIMS-specific
    if dir_type == 'deims':
        potential_composites = os.listdir(directory+'/composites')
        composites = {}
        for x in potential_composites:
            try:
                composite = gpd.read_file(f'{directory}/composites/{x}')
            except:
                try:
                    composite = gpd.read_file(f'zip://{directory}/composites/{x}/boundaries.shp.zip')
                except:
                    continue
            composites[x] = composite

        return {
                'metadata': metadata,
                'boundaries': boundaries,
                'composites': composites,
                }

    # zone-specific
    else:
        if dir_type == 'nat-zone':
            return {
                    'metadata': metadata,
                    'boundaries': boundaries,
                    'nat_zone_group': nat_zone_group,
                }
        else:
            return {
                    'metadata': metadata,
                    'boundaries': boundaries,
                    'nat_zone_group': None,
                    }


# useful wrapper
def loadAllInfo(sf_root):
    """Run this on app startup to compile available stuff into dicts"""
    validated_zones = {}
    validated_deims_sites = {}

    # we'll search these directories for data
    nuts_zone_dirs = os.listdir(f'{sf_root}/zones/nuts')
    lau_zone_dirs = os.listdir(f'{sf_root}/zones/lau')
    national_zone_dirs = os.listdir(f'{sf_root}/zones/national')
    deims_sites_to_try = os.listdir(f'{sf_root}/deims/')
    # nuts directories will contain these subdirectories
    nuts_level_dir_names = ['nuts0','nuts1','nuts2','nuts3']

    # try to load each NUTS zone...
    for x in nuts_zone_dirs:
        for y in nuts_level_dir_names:
            z = loadDirectory(f'{sf_root}/zones/nuts/{x}/{y}','eu-zone',['displayName','IDColumn','nameColumn'],True)
            title = x + '-' + y[-1]
            validated_zones[title] = z

    # ...try to load each LAU zone...
    for x in lau_zone_dirs:
        z = loadDirectory(f'{sf_root}/zones/lau/{x}','eu-zone',['displayName','IDColumn','nameColumn'],True)
        validated_zones[x] = z

    # ...try to load each national zone...
    for x in national_zone_dirs:
        for y in os.listdir(f'{sf_root}/zones/national/{x}'):
            z = loadDirectory(f'{sf_root}/zones/national/{x}/{y}','nat-zone',['displayName'],False,x)
            validated_zones[y] = z

    # ...try to load each DEIMS site
    for x in deims_sites_to_try:
        z = loadDirectory(f'{sf_root}/deims/{x}','deims',['id','displayName','nationalZonesAvailable'],True)
        validated_deims_sites[x] = z

    return (validated_zones,validated_deims_sites)
