from shapely.geometry import shape, mapping, MultiPolygon, LineString, MultiLineString
from shapely.ops import shared_paths
from shapely.geometry.base import BaseGeometry
from shapely.ops import cascaded_union
from enum import Enum
from math import atan2, degrees, pi, cos, sin, asin, sqrt, radians
from json import dumps


# On Windows, I needed to install Shapely manually
# Found whl file here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
# And then ran:
# from pip._internal import main
# def install_whl(path):
#     main(['install', path])
# install_whl("path_to_file\\Shapely-1.6.4.post1-cp37-cp37m-win32.whl")
# but not sure if this worked...
from exportData.displayShapes import plotRedistrictingGroups


def convertGeoJSONToShapely(geoJSON):
    shapelyShape = shape(geoJSON)
    return shapelyShape


def intersectingGeometries(a, b):
    return a.geometry.intersects(b.geometry)


def doesEitherGeographyContainTheOther(a, b):
    aContainsBBoundary = doesGeographyContainTheOther(container=a, target=b)
    bContainsABoundary = doesGeographyContainTheOther(container=b, target=a)
    return aContainsBBoundary or bContainsABoundary


def doesGeographyContainTheOther(container, target):
    if type(container.geometry) is MultiPolygon:
        containerPolygons = list(container.geometry)
    else:
        containerPolygons = [container.geometry]

    containsTargetBoundary = False
    for containerPolygon in containerPolygons:
        if containerPolygon.interiors:
            containsTargetBoundary = containsTargetBoundary or containerPolygon.boundary.contains(target.geometry.boundary)
        else:
            containsTargetBoundary = containsTargetBoundary or containerPolygon.contains(target.geometry)
    return containsTargetBoundary


def isBoundaryGeometry(parent, child):
    return parent.geometry.boundary.intersects(child.geometry.boundary)


def geometryFromMultipleGeometries(geometryList):
    polygons = [geometry.geometry for geometry in geometryList]
    return geometryFromMultiplePolygons(polygons)


def geometryFromMultiplePolygons(polygonList):
    union = cascaded_union(polygonList)
    union = union.simplify(tolerance=0.0) #to remove excessive points
    return union


class CardinalDirection(Enum):
    north = 1
    west = 3
    east = 0
    south = 4


class Alignment(Enum):
    northSouth = 1
    westEast = 2


def findDirection(basePoint, targetPoint):
    if basePoint == targetPoint:
        return CardinalDirection.north

    xDiff = targetPoint.x - basePoint.x
    yDiff = targetPoint.y - basePoint.y
    radianDiff = atan2(yDiff, xDiff)

    # rotate 90 degrees for easier angle matching
    radianDiff = radianDiff - (pi / 2)

    if radianDiff < 0:
        radianDiff = radianDiff + (2 * pi)

    degDiff = degrees(radianDiff)

    if 45 <= degDiff and degDiff < 135:
        return CardinalDirection.west
    elif 135 <= degDiff and degDiff < 225:
        return CardinalDirection.south
    elif 225 <= degDiff and degDiff < 315:
        return CardinalDirection.east
    else:
        return CardinalDirection.north


def findDirectionOfShape(baseShape, targetShape):
    basePoint = baseShape.centroid
    targetPoint = targetShape.centroid
    direction = findDirection(basePoint=basePoint, targetPoint=targetPoint)
    return direction


def findDirectionOfShapeFromPoint(basePoint, targetShape):
    targetPoint = targetShape.centroid
    direction = findDirection(basePoint=basePoint, targetPoint=targetPoint)
    return direction


def findDirectionOfBorderGeometries(parentShape, targetShapes):
    directionOfShapes = []
    parentLines = getLineListFromBoundary(parentShape.geometry.boundary)
    for targetShape in targetShapes:
        edgesInCommon = []
        for parentLine in parentLines:
            targetLines = getLineListFromBoundary(targetShape.geometry.boundary)
            for targetLine in targetLines:
                edgesInCommon.append(shared_paths(parentLine, targetLine))
        commomEdgeShape = geometryFromMultiplePolygons(edgesInCommon)
        direction = findDirectionOfShape(baseShape=targetShape.geometry.centroid, targetShape=commomEdgeShape)
        directionOfShapes.append((targetShape, direction))
    return directionOfShapes


def mostCardinalOfGeometries(geometryList, direction):
    if direction is CardinalDirection.north:
        return max(geometryList, key=lambda geometry: geometry.geometry.bounds[3])
    elif direction is CardinalDirection.east:
        return max(geometryList, key=lambda geometry: geometry.geometry.bounds[2])
    elif direction is CardinalDirection.south:
        return min(geometryList, key=lambda geometry: geometry.geometry.bounds[1])
    elif direction is CardinalDirection.west:
        return min(geometryList, key=lambda geometry: geometry.geometry.bounds[0])


def getLineListFromBoundary(boundary):
    lineList = []
    if type(boundary) is MultiLineString:
        lineList = boundary.geoms
    elif type(boundary) is LineString:
        lineList.append(boundary)
    return lineList


def shapelyGeometryToGeoJSON(geometry):
    geoDict = mapping(geometry)
    geoString = dumps(geoDict)
    return geoString


def distanceBetweenGeometries(a, b):
    if type(a) is list:
        a = geometryFromMultipleGeometries(a)
    elif isinstance(a, BaseGeometry):
        a = a
    else:
        a = a.geometry

    if type(b) is list:
        b = geometryFromMultipleGeometries(b)
    elif isinstance(b, BaseGeometry):
        b = b
    else:
        b = b.geometry
    return a.distance(b)


def findClosestGeometry(originGeometry, otherGeometries):
    candidateGeometries = [block for block in otherGeometries if block is not originGeometry]
    distanceDict = {}
    for candidateGeometry in candidateGeometries:
        distance = distanceBetweenGeometries(originGeometry, candidateGeometry)
        distanceDict[distance] = candidateGeometry
    shortestDistance = min(distanceDict.keys())
    closestGeometry = distanceDict[shortestDistance]
    return closestGeometry


def findContiguousGroupsOfGraphObjects(graphObjects):
    if graphObjects:
        remainingObjects = graphObjects.copy()
        contiguousObjectGroups = []
        while len(remainingObjects) > 0:
            contiguousObjectGroups.append(floodFillGraphObject(remainingObjects=remainingObjects))
        return contiguousObjectGroups
    else:
        return []


def floodFillGraphObject(remainingObjects):
    floodFilledObjects = []
    floodQueue = []
    floodQueue.append(remainingObjects[0])

    while len(floodQueue) > 0:
        graphObject = floodQueue.pop(0)
        remainingObjects.remove(graphObject)
        floodFilledObjects.append(graphObject)

        directionSets = graphObject.directionSets
        for directionSet in directionSets:
            for neighborObject in directionSet:
                if neighborObject in remainingObjects and neighborObject not in floodQueue:
                    floodQueue.append(neighborObject)

    return floodFilledObjects


def alignmentOfPolygon(polygon):
    minX = polygon.bounds[0]
    minY = polygon.bounds[1]
    maxX = polygon.bounds[2]
    maxY = polygon.bounds[3]
    boxDimensions = getWidthAndHeightOfBoxOnEarth(minX=minX, minY=minY, maxX=maxX, maxY=maxY)
    if boxDimensions[0] < boxDimensions[1]:
        return Alignment.northSouth
    else:
        return Alignment.westEast


def getWidthAndHeightOfBoxOnEarth(minX, minY, maxX, maxY):
    aWidth = getDistanceBetweenLatLong(lat1=minY, lon1=maxX, lat2=maxY, lon2=maxX)
    bWidth = getDistanceBetweenLatLong(lat1=minY, lon1=minX, lat2=maxY, lon2=minX)
    maxWidth = max(aWidth, bWidth)
    aHeight = getDistanceBetweenLatLong(lat1=minX, lon1=maxY, lat2=maxX, lon2=maxY)
    bHeight = getDistanceBetweenLatLong(lat1=minX, lon1=minY, lat2=maxX, lon2=minY)
    maxHeight = max(aHeight, bHeight)
    return (maxWidth, maxHeight)


def getDistanceBetweenLatLong(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km