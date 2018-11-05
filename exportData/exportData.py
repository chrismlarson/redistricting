from shapely.geometry import mapping
from os import path, makedirs
import glob
import pickle
from tqdm import tqdm
# import fiona
import sys

# def exportGeographiesToShapefile(geographyList, descriptionOfInfo):
#     # Define a polygon feature geometry with one attribute
#     schema = {
#         'geometry': 'Polygon',
#         'properties': {'id': 'int'},
#     }
#
#     countyShapeDataPath = path.expanduser('~/Documents/{0}.shp'.format(descriptionOfInfo))
#
#     # Write a new Shapefile
#     with fiona.open(countyShapeDataPath, 'w', 'ESRI Shapefile', schema) as c:
#         id = 0
#         for geoToExport in geographyList:
#             if hasattr(geoToExport, 'FIPS'):
#                 id = geoToExport.FIPS
#             else:
#                 id = id+1
#             c.write({
#                 'geometry': mapping(geoToExport.geometry),
#                 'properties': {'id': id},
#             })

def saveDataToDirectoryWithDescription(data, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    count = 1
    for dataChunk in data:
        filePath = '{0}/{1:09}.redistdata'.format(directoryPath, count)
        saveDataToFile(data=dataChunk, filePath=filePath)
        count += 1


def saveDataToFileWithDescription(data, censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser('~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    saveDataToFile(data=data, filePath=filePath)


def saveDataToFile(data, filePath):
    sys.setrecursionlimit(100000)
    with open(filePath, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    tqdm.write('*** Saved: {0} ***'.format(filePath))


def loadDataFromDirectoryWithDescription(censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    data = []
    for fileName in glob.glob('{0}/*.redistdata'.format(directoryPath)):
        data.append(loadDataFromFile(fileName))
    return data


def loadDataFromFileWithDescription(censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser('~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    return loadDataFromFile(filePath)


def loadDataFromFile(filePath):
    with open(filePath, 'rb') as file:
        data = pickle.load(file)
    return data