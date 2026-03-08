from shapely.geometry import mapping, Polygon, MultiPolygon
from collections import OrderedDict
from os import path, makedirs
import glob
import pickle
import json
from tqdm import tqdm
from geographyHelper import shapelyGeometryToGeoJSON
import sys


def saveDataToDirectoryWithDescription(data, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser(f'~/Documents/{censusYear}-{stateName}-{descriptionOfInfo}Info')
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    for count, dataChunk in enumerate(data, start=1):
        filePath = f'{directoryPath}/{count:09}.redistdata'
        saveDataToFile(data=dataChunk, filePath=filePath)


def saveDataToFileWithDescription(data, censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser(f'~/Documents/{censusYear}-{stateName}-{descriptionOfInfo}Info.redistdata')
    saveDataToFile(data=data, filePath=filePath)


def saveDataToFile(data, filePath):
    tqdm.write(f'*** Attempting to save: {filePath} ***')
    sys.setrecursionlimit(100000)
    with open(filePath, 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    tqdm.write(f'*** Saved: {filePath} ***')


def saveGeoJSONToDirectoryWithDescription(geographyList, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser(f'~/Documents/{censusYear}-{stateName}-{descriptionOfInfo}Info')
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    geoJSONObjects = []
    for geography in geographyList:
        if isinstance(geography.geometry, MultiPolygon):
            exteriors = [Polygon(polygon.exterior) for polygon in geography.geometry.geoms]
            exteriorPolygon = MultiPolygon(exteriors)
        else:
            exteriorPolygon = Polygon(geography.geometry.exterior)
        exteriorJSON = shapelyGeometryToGeoJSON(exteriorPolygon)
        geoJSONObjects.append(exteriorJSON)
    for count, jsonString in enumerate(geoJSONObjects, start=1):
        filePath = f'{directoryPath}/{count:04}.geojson'
        tqdm.write(f'*** Attempting to save: {filePath} ***')
        jsonObject = json.loads(jsonString)
        jsonObject['properties'] = {'number': str(count)}
        jsonObject = OrderedDict([('type', jsonObject['type']),
                                  ('properties', jsonObject['properties']),
                                  ('coordinates', jsonObject['coordinates'])])
        jsonString = json.dumps(jsonObject)
        with open(filePath, 'w') as jsonFile:
            print(jsonString, file=jsonFile)
        tqdm.write(f'*** Saved: {filePath} ***')


def loadDataFromDirectoryWithDescription(censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser(f'~/Documents/{censusYear}-{stateName}-{descriptionOfInfo}Info')
    redistFilesInDirectory = sorted(glob.glob(f'{directoryPath}/*.redistdata'))
    return [loadDataFromFile(fileName) for fileName in redistFilesInDirectory]


def loadDataFromFileWithDescription(censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser(f'~/Documents/{censusYear}-{stateName}-{descriptionOfInfo}Info.redistdata')
    return loadDataFromFile(filePath)


def loadDataFromFile(filePath):
    tqdm.write(f'*** Attempting to load: {filePath} ***')
    with open(filePath, 'rb') as file:
        data = pickle.load(file)
    tqdm.write(f'*** Loaded: {filePath} ***')
    return data
