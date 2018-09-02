import json
from esridump.dumper import EsriDumper

#blockGeometries = EsriDumper('https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14', extra_query_args={'where': 'STATE=\'26\' AND COUNTY=\'065\''}) #get all blocks in Ingham County, MI (fips:065)
blockGeometries = EsriDumper('https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14', extra_query_args={'where': 'STATE=\'26\'','orderByFields':'COUNTY'}) #get all blocks in Michigan (fips:26)

#https://github.com/openaddresses/pyesridump

# Iterate over each feature
for blockGeometry in blockGeometries:
    print(json.dumps(blockGeometry))