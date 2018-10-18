from shapely.geometry import mapping
from os import path
import pickle
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
        id = 0
        for geoToExport in geographyList:
            if hasattr(geoToExport, 'FIPS'):
                id = geoToExport.FIPS
            else:
                id = id+1
            c.write({
                'geometry': mapping(geoToExport.geometry),
                'properties': {'id': id},
            })


def saveDataToFile(data, censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser('~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    pickle.dump(data, open(filePath, 'wb'))


def loadDataFromFile(filePath):
    data = pickle.load(open(filePath, 'rb'))
    return data