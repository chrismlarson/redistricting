from shapely.geometry import shape, mapping, Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import shared_paths, nearest_points, cascaded_union
from enum import Enum
from math import atan2, degrees, pi, cos, sin, asin, sqrt, radians, pow
from json import dumps
from itertools import groupby
from tqdm import tqdm
from exportData.displayShapes import plotGraphObjectGroups


# On Windows, I needed to install Shapely manually
# Found whl file here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
# And then ran:
# from pip._internal import main
# def install_whl(path):
#     main(['install', path])
# install_whl("path_to_file\\Shapely-1.6.4.post1-cp37-cp37m-win32.whl")
# but not sure if this worked...


def convertGeoJSONToShapely(geoJSON):
    shapelyShape = shape(geoJSON)
    return shapelyShape


def intersectingGeometries(a, b):
    return intersectingPolygons(a.geometry, b.geometry)


def intersectingPolygons(a, b):
    # are they touching?
    if a.intersects(b):
        # does one contain the other?
        if doesEitherPolygonContainTheOther(a, b):
            return True
        else:
            # do they touch by just a point or do they share an edge?
            return len(findCommonEdges(a, b)) > 0
    else:
        return False


def doesEitherGeographyContainTheOther(a, b):
    aContainsBBoundary = doesGeographyContainTheOther(container=a, target=b)
    bContainsABoundary = doesGeographyContainTheOther(container=b, target=a)
    return aContainsBBoundary or bContainsABoundary


def doesEitherPolygonContainTheOther(a, b):
    aContainsBBoundary = doesPolygonContainTheOther(container=a, target=b)
    bContainsABoundary = doesPolygonContainTheOther(container=b, target=a)
    return aContainsBBoundary or bContainsABoundary


def getPolygonThatIntersectsGeometry(polygonList, targetGeometry):
    for polygon in polygonList:
        if intersectingPolygons(polygon, targetGeometry.geometry):
            return polygon
    return None


def getPolygonThatContainsGeometry(polygonList, targetGeometry, useTargetRepresentativePoint=False,
                                   ignoreInteriors=True):
    for polygon in polygonList:
        if doesPolygonContainTheOther(container=polygon,
                                      target=targetGeometry.geometry,
                                      ignoreInteriors=ignoreInteriors,
                                      useTargetRepresentativePoint=useTargetRepresentativePoint):
            return polygon
    return None


def doesGeographyContainTheOther(container, target, useTargetRepresentativePoint=False):
    containsTargetBoundary = doesPolygonContainTheOther(container=container.geometry,
                                                        target=target.geometry,
                                                        useTargetRepresentativePoint=useTargetRepresentativePoint)
    return containsTargetBoundary


def doesPolygonContainTheOther(container, target, ignoreInteriors=True, useTargetRepresentativePoint=False):
    if type(container) is MultiPolygon:
        containerPolygons = list(container)
    else:
        containerPolygons = [container]
    containsTarget = False
    for containerPolygon in containerPolygons:
        if containerPolygon.interiors and ignoreInteriors:
            # MultiLineStrings don't work well with the "contains" method
            containerPolygonBoundary = containerPolygon.boundary
            if type(containerPolygonBoundary) is MultiLineString:
                containerPolygonBoundary = containerPolygonBoundary.convex_hull
            targetBoundary = target.boundary
            if type(targetBoundary) is MultiLineString:
                targetBoundary = targetBoundary.convex_hull

            if useTargetRepresentativePoint:
                containsTarget = containsTarget or containerPolygonBoundary.contains(target.representative_point())
            else:
                containsTarget = containsTarget or containerPolygonBoundary.contains(targetBoundary)
        else:
            if useTargetRepresentativePoint:
                containsTarget = containsTarget or containerPolygon.contains(target.representative_point())
            else:
                containsTarget = containsTarget or containerPolygon.contains(target)
    return containsTarget


def isBoundaryGeometry(parent, child):
    if type(parent.geometry) is MultiPolygon:
        containerPolygons = list(parent.geometry)
    else:
        containerPolygons = [parent.geometry]
    isChildBoundaryGeometry = False
    for containerPolygon in containerPolygons:
        isChildBoundaryGeometry = isChildBoundaryGeometry or containerPolygon.exterior.intersects(
            child.geometry.boundary)
    return isChildBoundaryGeometry


def polygonFromMultipleGeometries(geometryList, useEnvelope=False, simplificationTolerance=0.0):
    polygons = [geometry.geometry for geometry in geometryList]
    return polygonFromMultiplePolygons(polygons,
                                       useEnvelope=useEnvelope,
                                       simplificationTolerance=simplificationTolerance)


def polygonFromMultiplePolygons(polygonList, useEnvelope=False, simplificationTolerance=0.0):
    if useEnvelope:
        polygonsToCombine = [polygon.envelope for polygon in polygonList]
    else:
        polygonsToCombine = polygonList
    union = cascaded_union(polygonsToCombine)
    union = union.simplify(tolerance=simplificationTolerance)  # to remove excessive points
    return union


class CardinalDirection(Enum):
    north = 1
    west = 3
    east = 0
    south = 4


class Alignment(Enum):
    northSouth = 1
    westEast = 2


def findCommonEdges(a, b):
    aLines = getLineListFromBoundary(a.boundary)
    edgesInCommon = []
    for aLine in aLines:
        bLines = getLineListFromBoundary(b.boundary)
        for bLine in bLines:
            edgesInCommon.append(shared_paths(aLine, bLine))

    edgesInCommon = [edge for edge in edgesInCommon if not edge.is_empty]
    return edgesInCommon


def findDirection(basePoint, targetPoint, topAngleFromCenter=45.0):
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

    northWestAngle = topAngleFromCenter
    southWestAngle = 180 - topAngleFromCenter
    southEastAngle = 180 + topAngleFromCenter
    northEastAngle = 360 - topAngleFromCenter

    if northWestAngle <= degDiff < southWestAngle:
        return CardinalDirection.west
    elif southWestAngle <= degDiff < southEastAngle:
        return CardinalDirection.south
    elif southEastAngle <= degDiff < northEastAngle:
        return CardinalDirection.east
    else:
        return CardinalDirection.north


def findDirectionOfShape(baseShape, targetShape):
    basePoint = baseShape.centroid
    targetPoint = targetShape.centroid
    dimensionsOfBaseShape = dimensionsOfPolygon(baseShape)
    topAngleFromCenterOfBaseShape = topAngleFromCenterOfRectangle(width=dimensionsOfBaseShape[0],
                                                                  height=dimensionsOfBaseShape[1])
    direction = findDirection(basePoint=basePoint, targetPoint=targetPoint,
                              topAngleFromCenter=topAngleFromCenterOfBaseShape)
    return direction


def findDirectionOfShapeFromPoint(basePoint, targetShape):
    targetPoint = targetShape.centroid
    direction = findDirection(basePoint=basePoint, targetPoint=targetPoint)
    return direction


def findDirectionOfBorderGeometries(parentGeometry, targetGeometries):
    directionOfShapes = []
    for targetGeometry in targetGeometries:
        edgesInCommon = findCommonEdges(parentGeometry.geometry, targetGeometry.geometry)

        if not edgesInCommon:  # means we intersect only at a point
            edgesInCommon = parentGeometry.geometry.boundary.intersection(targetGeometry.geometry.boundary)

        commonEdgeShape = polygonFromMultiplePolygons(edgesInCommon)
        direction = findDirectionOfShape(baseShape=parentGeometry.geometry, targetShape=commonEdgeShape)
        directionOfShapes.append((targetGeometry, direction))
    return directionOfShapes


def topAngleFromCenterOfRectangle(width, height):
    sideAngle = atan2(width, height)

    if sideAngle < 0:
        sideAngle = sideAngle + (2 * pi)

    sideAngleDegrees = degrees(sideAngle)
    return sideAngleDegrees


def mostCardinalOfGeometries(geometryList, direction):
    boundsIndex = boundsIndexFromDirection(direction)
    if direction is CardinalDirection.north or direction is CardinalDirection.east:
        return max(geometryList, key=lambda geometry: geometry.geometry.bounds[boundsIndex])
    else:
        return min(geometryList, key=lambda geometry: geometry.geometry.bounds[boundsIndex])


def boundsIndexFromDirection(direction):
    if direction is CardinalDirection.north:
        return 3
    elif direction is CardinalDirection.east:
        return 2
    elif direction is CardinalDirection.south:
        return 1
    elif direction is CardinalDirection.west:
        return 0


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
        a = polygonFromMultipleGeometries(a)
    elif isinstance(a, BaseGeometry):
        a = a
    else:
        a = a.geometry

    if type(b) is list:
        b = polygonFromMultipleGeometries(b)
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


def forestFireFillGraphObject(candidateObjects, startingObject=None, notInList=None):
    fireFilledObjects = []
    fireQueue = []
    if not startingObject:
        startingObject = candidateObjects[0]
    fireQueue.append(startingObject)

    while len(fireQueue) > 0:
        graphObject = fireQueue.pop(0)
        candidateObjects.remove(graphObject)
        fireFilledObjects.append(graphObject)

        for neighborObject in graphObject.allNeighbors:
            if neighborObject in candidateObjects and neighborObject not in fireQueue:
                if notInList is None or neighborObject not in notInList:
                    fireQueue.append(neighborObject)

    return fireFilledObjects


def weightedForestFireFillGraphObject(candidateObjects,
                                      startingObjects=None,
                                      condition=lambda x, y: (True, 0),
                                      weightingScore=lambda w, x, y, z: 1,
                                      shouldDrawEachStep=False,
                                      returnBestCandidateGroup=True,
                                      fastCalculations=True):
    bestGraphObjectCandidateGroupThisPass = None
    offCount = 0
    candidateGroupsThatDidNotMeetConditionThisPass = []
    fireFilledObjects = []
    fireQueue = []
    remainingObjects = candidateObjects.copy()
    if not startingObjects:
        # this doesn't occur during the forest fire fill when creating districts
        startingObjects = [remainingObjects[0]]
    fireQueue.append(startingObjects)

    count = 1
    with tqdm() as pbar:
        while len(fireQueue) > 0:
            pbar.update(1)
            pbar.set_description(
                'FireFilled: {0} - FireQueue: {1} - Remaining: {2} - Off count: {3}'.format(
                    len(fireFilledObjects), len(fireQueue), len(remainingObjects), offCount))

            # pull from the top of the queue
            graphObjectCandidateGroup = fireQueue.pop(0)

            # remove objects that we pulled from the queue from the remaining list
            remainingObjects = [object for object in remainingObjects if object not in graphObjectCandidateGroup]

            if shouldDrawEachStep:
                plotGraphObjectGroups([fireFilledObjects, graphObjectCandidateGroup, remainingObjects],
                                      showDistrictNeighborConnections=True,
                                      saveImages=True,
                                      saveDescription='WeightedForestFireFillGraphObject-{0}-{1}'.format(
                                          id(candidateObjects), count))
                count += 1

            potentiallyIsolatedGroups = findContiguousGroupsOfGraphObjects(remainingObjects)
            if len(potentiallyIsolatedGroups) <= 1:  # candidate won't block any other groups
                conditionResult = condition(fireFilledObjects, graphObjectCandidateGroup)
                if conditionResult[0]:
                    offCount = conditionResult[1]
                    fireFilledObjects.extend(graphObjectCandidateGroup)
                    bestGraphObjectCandidateGroupThisPass = None  # set this back to none when we add something
                    candidateGroupsThatDidNotMeetConditionThisPass = []  # clear this when we add something

                    # find any of objects just added and remove them from the queue
                    remainingItemsFromGroups = []
                    groupsToRemove = []
                    for queueItemGroup in fireQueue:
                        if any([queueItem for queueItem in queueItemGroup if queueItem in graphObjectCandidateGroup]):
                            remainingItems = [queueItem for queueItem in queueItemGroup if
                                              queueItem not in graphObjectCandidateGroup]
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
                        for neighborObject in graphObjectCandidate.allNeighbors:
                            flatFireQueue = [graphObject for graphObjectGroup in fireQueue
                                             for graphObject in graphObjectGroup]
                            if neighborObject in remainingObjects and neighborObject not in flatFireQueue:
                                fireQueue.append([neighborObject])

                    # if we don't need to return the next best candidate, we can remove groups from the queue
                    # that don't meet the condition right now to speed up processing
                    if not returnBestCandidateGroup:
                        fireQueue = [fireQueueGroup for fireQueueGroup in fireQueue if
                                     condition(fireFilledObjects, fireQueueGroup)[0]]
                else:
                    if returnBestCandidateGroup and bestGraphObjectCandidateGroupThisPass is None:
                        if all([len(graphObjectCandidate.children) > 1
                                for graphObjectCandidate in graphObjectCandidateGroup]):
                            bestGraphObjectCandidateGroupThisPass = graphObjectCandidateGroup

                    remainingObjects.extend(graphObjectCandidateGroup)
                    candidateGroupsThatDidNotMeetConditionThisPass.append(graphObjectCandidateGroup)
            else:
                # find the contiguous group with largest population and remove.
                # This everything else and will be handled by subsequent fire fill passes
                potentiallyIsolatedGroups.sort(key=lambda x: sum(group.population for group in x), reverse=True)
                potentiallyIsolatedGroups.remove(potentiallyIsolatedGroups[0])
                potentiallyIsolatedObjects = [group for groupList in potentiallyIsolatedGroups for group in groupList]

                conditionResult = condition(fireFilledObjects, potentiallyIsolatedObjects + graphObjectCandidateGroup)
                if conditionResult[0]:
                    if shouldDrawEachStep:
                        plotGraphObjectGroups(
                            [fireFilledObjects, graphObjectCandidateGroup, remainingObjects,
                             potentiallyIsolatedObjects],
                            showDistrictNeighborConnections=True,
                            saveImages=True,
                            saveDescription='WeightedForestFireFillGraphObject-{0}-{1}'.format(id(candidateObjects),
                                                                                               count))
                        count += 1

                    # add the potentially isolated groups and the candidate group back to the queue
                    combinationsOfPotentiallyIsolatedObjects = combinationsFromGroup(
                        candidateGroups=potentiallyIsolatedObjects,
                        mustTouchGroup=fireFilledObjects,
                        startingGroup=graphObjectCandidateGroup)

                    # make sure the combinations have at least one neighbor to the current fireFilledObjects
                    verifiedCombinations = []
                    for combinationOfPotentiallyIsolatedObjects in combinationsOfPotentiallyIsolatedObjects:
                        if any(comboGroupNeighbor in fireFilledObjects
                               for comboGroup in combinationOfPotentiallyIsolatedObjects
                               for comboGroupNeighbor in comboGroup.allNeighbors):
                            verifiedCombinations.append(combinationOfPotentiallyIsolatedObjects)

                    # make sure we don't add anything to the queue that's already been ruled out this pass
                    verifiedCombinations = [combination for combination in verifiedCombinations
                                            if combination not in candidateGroupsThatDidNotMeetConditionThisPass]

                    fireQueue.extend(verifiedCombinations)
                else:
                    candidateGroupsThatDidNotMeetConditionThisPass.append(graphObjectCandidateGroup)

                remainingObjects.extend(graphObjectCandidateGroup)  # add candidate back to the queue

            # remove duplicates from the list
            fireQueue.sort()
            fireQueue = list(fireQueueItem for fireQueueItem, _ in groupby(fireQueue))

            # apply weights for sorting
            weightedQueue = []
            fireFilledObjectsShape = polygonFromMultipleGeometries(fireFilledObjects)
            for queueObjectGroup in fireQueue:
                weightScore = weightingScore(fireFilledObjectsShape, remainingObjects, queueObjectGroup,
                                             fastCalculations)
                weightedQueue.append((queueObjectGroup, weightScore))

            # sort queue
            weightedQueue.sort(key=lambda x: x[1], reverse=True)
            fireQueue = [x[0] for x in weightedQueue]

    if shouldDrawEachStep:
        plotGraphObjectGroups(
            [fireFilledObjects, [], remainingObjects],
            showDistrictNeighborConnections=True,
            saveImages=True,
            saveDescription='WeightedForestFireFillGraphObject-{0}-{1}'.format(id(candidateObjects), count))

    return fireFilledObjects, bestGraphObjectCandidateGroupThisPass


def combinationsFromGroup(candidateGroups, mustTouchGroup, startingGroup):
    combinations = []

    # if the group is touching a must touch object, continue, otherwise add group plus all candidates
    mustTouchGroupNeighbors = [mustTouchObjectNeighbor for mustTouchObject in mustTouchGroup for mustTouchObjectNeighbor
                               in mustTouchObject.allNeighbors]
    if any(group for group in startingGroup if group in mustTouchGroupNeighbors):

        neighborsInCandidates = [groupNeighbor for group in startingGroup for groupNeighbor in group.allNeighbors if
                                 groupNeighbor in candidateGroups]
        if len(neighborsInCandidates) > 0:
            for neighbor in neighborsInCandidates:
                neighborCombinations = combinationsFromGroup(
                    candidateGroups=[candidateGroup for candidateGroup in candidateGroups if
                                     candidateGroup not in startingGroup and candidateGroup is not neighbor],
                    mustTouchGroup=mustTouchGroup,
                    startingGroup=[neighbor])
                for neighborCombination in neighborCombinations:
                    # add the combination with the group and without
                    neighborCombination.sort()
                    combinations.append(neighborCombination)
                    neighborCombinationWithGroup = neighborCombination + startingGroup
                    neighborCombinationWithGroup.sort()
                    combinations.append(neighborCombinationWithGroup)
        else:
            combinations.append(startingGroup)
    else:
        candidatesLeftWithGroup = candidateGroups + startingGroup
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
    boxDimensions = dimensionsOfPolygon(polygon)
    if boxDimensions[0] < boxDimensions[1]:
        return Alignment.northSouth
    else:
        return Alignment.westEast


def dimensionsOfPolygon(polygon):
    minLon = polygon.bounds[0]
    minLat = polygon.bounds[1]
    maxLon = polygon.bounds[2]
    maxLat = polygon.bounds[3]
    boxDimensions = getWidthAndHeightOfBoxOnEarth(minLat=minLat, minLon=minLon, maxLat=maxLat, maxLon=maxLon)
    return boxDimensions


def getWidthAndHeightOfBoxOnEarth(minLat, minLon, maxLat, maxLon):
    aWidth = getDistanceBetweenLatLong(lat1=minLon, lon1=maxLat, lat2=maxLon, lon2=maxLat)
    bWidth = getDistanceBetweenLatLong(lat1=minLon, lon1=minLat, lat2=maxLon, lon2=minLat)
    maxWidth = max(aWidth, bWidth)
    aHeight = getDistanceBetweenLatLong(lat1=minLat, lon1=maxLon, lat2=maxLat, lon2=maxLon)
    bHeight = getDistanceBetweenLatLong(lat1=minLat, lon1=minLon, lat2=maxLat, lon2=minLon)
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


def simplifyPolygonsBasedOnAnotherPolygon(polygonsToSimplify, referencePolygon):
    simplifiedPolygons = []
    with tqdm(total=len(polygonsToSimplify)) as pbar:
        for polygonToSimplify in polygonsToSimplify:
            snappedPolygon = snapPolygonToPolygon(polygonToSimplify, referencePolygon, tolerance=0.05)
            simplifiedPolygon = snappedPolygon.simplify(tolerance=0.0)  # remove excess points
            simplifiedPolygons.append(simplifiedPolygon)
            pbar.update(1)
    return simplifiedPolygons


def snapPolygonToPolygon(polygonToSnap, referencePolygon, tolerance):
    coordinates = []
    for x, y in polygonToSnap.exterior.coords:  # for each vertex in the first polygon
        point = Point(x, y)
        p1, p2 = nearest_points(point, referencePolygon)  # find the nearest point on the second polygon

        if p1.distance(p2) <= tolerance:
            # it's within the snapping tolerance, use the snapped vertex
            coordinates.append(p2.coords[0])
        else:
            # it's too far, use the original vertex
            coordinates.append((x, y))
    # convert coordinates back to a Polygon and return
    return Polygon(coordinates)
