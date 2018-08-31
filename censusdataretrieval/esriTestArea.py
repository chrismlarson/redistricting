import json
from esridump.dumper import EsriDumper

blockGeometries = EsriDumper("https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14") #works but is too much
#blockGeometries = EsriDumper("https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14/filter?filtersArray={filtersArray:[{singleAttributeFilter:[{fieldName:\"STATE\",fieldValue:\"26\"}]}]}") #trying to get filter to work, but no dice yet.

#https://github.com/openaddresses/pyesridump

# Iterate over each feature
for blockGeometry in blockGeometries:
    print(json.dumps(blockGeometry))