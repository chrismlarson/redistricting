from shapely.geometry import mapping
from os import path
import fiona

def exportGeographiesToShapefile(geographyList, descriptionOfInfo):
    # Define a polygon feature geometry with one attribute
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int'},
    }

    countyShapeDataPath = path.expanduser('~/Documents/{0}.shp'.format(descriptionOfInfo))

    # Write a new Shapefile
    with fiona.open(countyShapeDataPath, 'w', 'ESRI Shapefile', schema) as c:
        for geoToExport in geographyList:
            c.write({
                'geometry': mapping(geoToExport.geometry),
                'properties': {'id': geoToExport.FIPS},
            })

