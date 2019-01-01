from shapely.geometry import mapping, Polygon, MultiPolygon
from collections import OrderedDict
from os import path, makedirs
import glob
import pickle
import json
from tqdm import tqdm
from geographyHelper import shapelyGeometryToGeoJSON
import sys
#import fiona

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
    tqdm.write('*** Attempting to save: {0} ***'.format(filePath))
    sys.setrecursionlimit(100000)
    with open(filePath, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    tqdm.write('*** Saved: {0} ***'.format(filePath))


def saveGeoJSONToDirectoryWithDescription(geographyList, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    geoJSONObjects = []
    for geography in geographyList:
        if type(geography.geometry) is MultiPolygon:
            exteriors = [Polygon(polygon.exterior) for polygon in geography.geometry]
            exteriorPolygon = MultiPolygon(exteriors)
        else:
            exteriorPolygon = Polygon(geography.geometry.exterior)
        exteriorJSON = shapelyGeometryToGeoJSON(exteriorPolygon)
        geoJSONObjects.append(exteriorJSON)
    count = 1
    for jsonString in geoJSONObjects:
        filePath = '{0}/{1:04}.geojson'.format(directoryPath, count)
        tqdm.write('*** Attempting to save: {0} ***'.format(filePath))
        jsonObject = json.loads(jsonString)
        numberProperty = {'number': '{0}'.format(count)}
        jsonObject['properties'] = numberProperty
        jsonObject = OrderedDict([('type', jsonObject['type']),
                                  ('properties', jsonObject['properties']),
                                  ('coordinates', jsonObject['coordinates'])])
        jsonString = json.dumps(jsonObject)
        with open(filePath, "w") as jsonFile:
            print(jsonString, file=jsonFile)
        tqdm.write('*** Saved: {0} ***'.format(filePath))
        count += 1


def loadDataFromDirectoryWithDescription(censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    data = []
    redistFilesInDirectory = glob.glob('{0}/*.redistdata'.format(directoryPath))
    redistFilesInDirectory.sort()
    for fileName in redistFilesInDirectory:
        data.append(loadDataFromFile(fileName))
    return data


def loadDataFromFileWithDescription(censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser('~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    return loadDataFromFile(filePath)


def loadDataFromFile(filePath):
    tqdm.write('*** Attempting to load: {0} ***'.format(filePath))
    with open(filePath, 'rb') as file:
        data = pickle.load(file)
        tqdm.write('*** Loaded: {0} ***'.format(filePath))
    return data