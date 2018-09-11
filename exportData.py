from shapely.geometry import mapping
from os import path
import fiona

def exportCountiesToShapefile(countyList):
    # Define a polygon feature geometry with one attribute
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int'},
    }

    countyShapeDataPath = path.expanduser('~/Documents/Counties.shp')

    # Write a new Shapefile
    with fiona.open(countyShapeDataPath, 'w', 'ESRI Shapefile', schema) as c:
        for county in countyList:
            c.write({
                'geometry': mapping(county.geometry),
                'properties': {'id': county.FIPS},
            })

