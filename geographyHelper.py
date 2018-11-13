from shapely.geometry import shape, mapping, MultiPolygon, LineString, MultiLineString
from shapely.ops import shared_paths
from shapely.geometry.base import BaseGeometry
from shapely.ops import cascaded_union
from enum import Enum
from math import atan2, degrees, pi, cos, sin, asin, sqrt, radians, pow
from json import dumps
from itertools import groupby

# On Windows, I needed to install Shapely manually
# Found whl file here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
# And then ran:
# from pip._internal import main
# def install_whl(path):
#     main(['install', path])
# install_whl("path_to_file\\Shapely-1.6.4.post1-cp37-cp37m-win32.whl")
# but not sure if this worked...
from exportData.displayShapes import plotRedistrictingGroups, plotDistrictCandidates


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
            containsTargetBoundary = containsTargetBoundary or containerPolygon.boundary.contains(
                target.geometry.boundary)
        else:
            containsTargetBoundary = containsTargetBoundary or containerPolygon.contains(target.geometry)
    return containsTargetBoundary


def isBoundaryGeometry(parent, child):
    return parent.geometry.boundary.intersects(child.geometry.boundary)


def geometryFromMultipleGeometries(geometryList, useEnvelope=False):
    if useEnvelope:
        polygons = [geometry.geometry.envelope for geometry in geometryList]
    else:
        polygons = [geometry.geometry for geometry in geometryList]
    return geometryFromMultiplePolygons(polygons)


def geometryFromMultiplePolygons(polygonList):
    union = cascaded_union(polygonList)
    union = union.simplify(tolerance=0.0)  # to remove excessive points
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


def findCommonEdges(a,b):
    aLines = getLineListFromBoundary(a.boundary)
    edgesInCommon = []
    for aLine in aLines:
        bLines = getLineListFromBoundary(b.boundary)
        for bLine in bLines:
            edgesInCommon.append(shared_paths(aLine, bLine))

    edgesInCommon = [edge for edge in edgesInCommon if not edge.is_empty]
    return edgesInCommon


def findDirectionOfBorderGeometries(parentShape, targetShapes):
    directionOfShapes = []
    for targetShape in targetShapes:
        edgesInCommon = findCommonEdges(parentShape.geometry, targetShape.geometry)

        if not edgesInCommon: #means we intersect only at a point
            edgesInCommon = parentShape.geometry.boundary.intersection(targetShape.geometry.boundary)

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
            contiguousObjectGroups.append(
                forestFireFillGraphObject(candidateObjects=remainingObjects))
        return contiguousObjectGroups
    else:
        return []


def forestFireFillGraphObject(candidateObjects):
    fireFilledObjects = []
    fireQueue = []
    fireQueue.append(candidateObjects[0])

    while len(fireQueue) > 0:
        graphObject = fireQueue.pop(0)
        candidateObjects.remove(graphObject)
        fireFilledObjects.append(graphObject)

        directionSets = graphObject.directionSets
        for directionSet in directionSets:
            for neighborObject in directionSet:
                if neighborObject in candidateObjects and neighborObject not in fireQueue:
                    fireQueue.append(neighborObject)

    return fireFilledObjects


def weightedForestFireFillGraphObject(candidateObjects,
                                      startingObject=None,
                                      condition=lambda x, y: True,
                                      weightingScore=lambda x, y, z: 1,
                                      shouldDrawEachStep=False):
    fireFilledObjects = []
    fireQueue = []
    remainingObjects = candidateObjects.copy()
    if not startingObject:
        startingObject = remainingObjects[0]
    fireQueue.append([startingObject])

    count = 1
    while len(fireQueue) > 0:
        # pull from the top of the queue
        graphObjectCandidateGroup = fireQueue.pop(0)

        # remove objects that we pulled from the queue from the remaining list
        remainingObjects = [object for object in remainingObjects if object not in graphObjectCandidateGroup]

        if shouldDrawEachStep:
            plotDistrictCandidates([fireFilledObjects, graphObjectCandidateGroup, remainingObjects],
                                   showDistrictNeighborConnections=True,
                                   saveImages=True,
                                   saveDescription='WeightedForestFireFillGraphObject{0}'.format(count))
            count += 1

        potentiallyIsolatedGroups = findContiguousGroupsOfGraphObjects(remainingObjects)
        if len(potentiallyIsolatedGroups) <= 1:  # candidate won't block any other groups
            if condition(fireFilledObjects, graphObjectCandidateGroup):
                fireFilledObjects.extend(graphObjectCandidateGroup)

                # find any of objects just added and remove them from the queue
                remainingItemsFromGroups = []
                groupsToRemove = []
                for queueItemGroup in fireQueue:
                    if any([queueItem for queueItem in queueItemGroup if queueItem in graphObjectCandidateGroup]):
                        remainingItems = [queueItem for queueItem in queueItemGroup if queueItem not in graphObjectCandidateGroup]
                        remainingItemsFromGroups.extend(remainingItems)
                        groupsToRemove.append(queueItemGroup)
                # remove duplicates from the lists
                remainingItemsFromGroups = set(remainingItemsFromGroups)
                # crazy way to remove duplicates from a list of lists
                groupsToRemove = [list(item) for item in set(tuple(row) for row in groupsToRemove)]
                for groupToRemove in groupsToRemove:
                    fireQueue.remove(groupToRemove)
                for remainingItemFromGroups in remainingItemsFromGroups:
                    fireQueue.append([remainingItemFromGroups])

                # add neighbors to the queue
                for graphObjectCandidate in graphObjectCandidateGroup:
                    directionSets = graphObjectCandidate.directionSets
                    for directionSet in directionSets:
                        for neighborObject in directionSet:
                            flatFireQueue = [object for objectGroup in fireQueue for object in objectGroup]
                            if neighborObject in remainingObjects and neighborObject not in flatFireQueue:
                                fireQueue.append([neighborObject])
            else:
                remainingObjects.extend(graphObjectCandidateGroup)
        else:
            # find the contiguous group with largest population and remove.
            # This will be handled by subsequent fire fill passes
            potentiallyIsolatedGroups.sort(key=lambda x: sum(group.population for group in x), reverse=True)
            potentiallyIsolatedGroups.remove(potentiallyIsolatedGroups[0])
            potentiallyIsolatedObjects = [group for groupList in potentiallyIsolatedGroups for group in groupList]

            if shouldDrawEachStep:
                plotDistrictCandidates([fireFilledObjects, graphObjectCandidateGroup, remainingObjects, potentiallyIsolatedObjects],
                                       showDistrictNeighborConnections=True,
                                       saveImages=True,
                                       saveDescription='WeightedForestFireFillGraphObject{0}'.format(count))
                count += 1

            # add the potentially isolated groups and the candidate group back to the queue
            combinationsOfPotentiallyIsolatedObjects = combinationsFromGroup(candidateGroups=potentiallyIsolatedObjects,
                                                                             mustTouchGroup=fireFilledObjects,
                                                                             startingGroup=graphObjectCandidateGroup)

            fireQueue.extend(combinationsOfPotentiallyIsolatedObjects)
            remainingObjects.extend(graphObjectCandidateGroup)  # add candidate back to the queue

        # remove duplicates from the list
        fireQueue.sort()
        fireQueue = list(fireQueueItem for fireQueueItem, _ in groupby(fireQueue))

        # apply weights for sorting
        weightedQueue = []
        for queueObjectGroup in fireQueue:
            weightScore = weightingScore(fireFilledObjects, remainingObjects, queueObjectGroup)
            weightedQueue.append((queueObjectGroup, weightScore))

        # sort queue
        weightedQueue.sort(key=lambda x: x[1], reverse=True)
        fireQueue = [x[0] for x in weightedQueue]

    return fireFilledObjects


def combinationsFromGroup(candidateGroups, mustTouchGroup, startingGroup):
    combinations = []

    for group in startingGroup:
        # if the group is touching a must touch object, continue, otherwise add group plus all candidates
        if group in [mustTouchObjectNeighbor for mustTouchObject in mustTouchGroup for mustTouchObjectNeighbor in mustTouchObject.allNeighbors]:
            neighborsInCandidates = [groupNeighbor for groupNeighbor in group.allNeighbors if groupNeighbor in candidateGroups]
            if len(neighborsInCandidates) > 0:
                for neighbor in neighborsInCandidates:
                    neighborCombinations = combinationsFromGroup(candidateGroups=[candidateGroup for candidateGroup in candidateGroups if candidateGroup is not group and candidateGroup is not neighbor],
                                                                 mustTouchGroup=mustTouchGroup,
                                                                 startingGroup=[neighbor])
                    for neighborCombination in neighborCombinations:
                        # add the combination with the group and without
                        neighborCombination.sort()
                        combinations.append(neighborCombination)
                        neighborCombinationWithGroup = neighborCombination + [group]
                        neighborCombinationWithGroup.sort()
                        combinations.append(neighborCombinationWithGroup)
            else:
                combinations.append([group])
        else:
            candidatesLeftWithGroup = candidateGroups + [group]
            candidatesLeftWithGroup.sort()
            combinations.append(candidatesLeftWithGroup)

    # remove duplicates from the list
    combinations.sort()
    combinations = list(combination for combination, _ in groupby(combinations))

    # make sure combinations are contiguous
    combinationsToRemove = []
    for combination in combinations:
        contiguousGroupsInCombination = findContiguousGroupsOfGraphObjects(combination)
        if len(contiguousGroupsInCombination) > 1:
            combinationsToRemove.append(combination)
    combinations = [combination for combination in combinations if combination not in combinationsToRemove]
    return combinations



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


def polsbyPopperScoreOfPolygon(polygon):
    # score= 4 * pi() * (area/(perimeter^2))
    return 4 * pi * (polygon.area / (pow(polygon.length, 2)))
