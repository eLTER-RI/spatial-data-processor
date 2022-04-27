"""Intended for use by Shiny only - relies on implicit imports."""


# read what DEIMS sites and zones are available from filesystem
validated_zones,validated_deims_sites = loadAllInfo('shapefiles')


# construct metadata for interface and workflows
# maps available site friendly names to IDs, the order required for shiny selectInputs
deims_site_name_mappings = {
        validated_deims_sites[x]['metadata']['displayName']: x for x in list(validated_deims_sites)
        }

# maps available site IDs to dict mapping available site composite friendly names to IDs
# enables discovering for each site what composites are available and how should they be presented
# essentially a dict of subdicts, where each subdict is structured the same as deims_site_name_mappings
deims_site_zone_options = {
        x: {
            validated_zones[y]['metadata']['displayName']: y for y in list(validated_deims_sites[x]['composites'])
            } for x in list(validated_deims_sites)
        }

# wrapper function to add site and update dictionaries in one go
def addSiteToInterface(deims_site_id_suffix):
    global validated_deims_sites
    global deims_site_name_mappings
    global deims_site_zone_options

    # create and save site
    new_site = getNewDeimsSite(deims_site_id_suffix,False)
    saveDeimsSite(new_site,'shapefiles/deims')

    # add metadata to global dicts
    validated_deims_sites[new_site['metadata']['id']['suffix']] = new_site
    deims_site_name_mappings[new_site['metadata']['displayName']] = new_site['metadata']['id']['suffix']
    # add sites
    deims_site_zone_options[new_site['metadata']['id']['suffix']] = {
            validated_zones[x]['metadata']['displayName']: x for x in list(new_site['composites'])
            }
