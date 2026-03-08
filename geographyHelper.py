from collections import deque
from shapely.geometry import shape, mapping, Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import shared_paths, nearest_points, unary_union
from geopy.distance import distance as distanceOnEarth
from enum import Enum
from math import atan2, degrees, pi, inf
from sys import float_info
from json import dumps
from itertools import groupby
from tqdm import tqdm
from exportData.displayShapes import plotGraphObjectGroups


def convertGeoJSONToShapely(geoJSON):
    return shape(geoJSON)


def intersectingGeometries(a, b):
    return intersectingPolygons(a.geometry, b.geometry)


def intersectingPolygons(a, b):
    # are they touching?
    if a.intersects(b):
        # does one contain the other?
        if doesEitherPolygonContainTheOther(a, b):
            return True
        # do they touch by just a point or do they share an edge?
        return len(findCommonEdges(a, b)) > 0
    return False


def allIntersectingPolygons(a, b):
    aPolygons = list(a.geoms) if isinstance(a, MultiPolygon) else [a]
    bPolygons = list(b.geoms) if isinstance(b, MultiPolygon) else [b]
    return all(intersectingPolygons(aPolygon, bPolygon)
               for aPolygon in aPolygons for bPolygon in bPolygons)


def doesEitherGeographyContainTheOther(a, b):
    return doesGeographyContainTheOther(container=a, target=b) or \
           doesGeographyContainTheOther(container=b, target=a)


def doesEitherPolygonContainTheOther(a, b):
    return doesPolygonContainTheOther(container=a, target=b) or \
           doesPolygonContainTheOther(container=b, target=a)


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
    return doesPolygonContainTheOther(container=container.geometry,
                                      target=target.geometry,
                                      useTargetRepresentativePoint=useTargetRepresentativePoint)


def doesPolygonContainTheOther(container, target, ignoreInteriors=True, useTargetRepresentativePoint=False):
    containerPolygons = list(container.geoms) if isinstance(container, MultiPolygon) else [container]
    targetPolygons = list(target.geoms) if isinstance(target, MultiPolygon) else [target]
    containsTarget = False
    for containerPolygon in containerPolygons:
        for targetPolygon in targetPolygons:
            if containerPolygon.interiors and ignoreInteriors:
                containerPolygonExterior = Polygon(containerPolygon.exterior)
                if useTargetRepresentativePoint:
                    containsTarget = containsTarget or containerPolygonExterior.contains(
                        targetPolygon.representative_point())
                else:
                    targetPolygonExterior = Polygon(targetPolygon.exterior)
                    containsTarget = containsTarget or containerPolygonExterior.contains(targetPolygonExterior)
            else:
                if useTargetRepresentativePoint:
                    containsTarget = containsTarget or containerPolygon.contains(targetPolygon.representative_point())
                else:
                    containsTarget = containsTarget or containerPolygon.contains(targetPolygon)
    return containsTarget


def isBoundaryGeometry(parent, child):
    containerPolygons = list(parent.geometry.geoms) if isinstance(parent.geometry, MultiPolygon) else [parent.geometry]
    return any(containerPolygon.exterior.intersects(child.geometry.boundary)
               for containerPolygon in containerPolygons)


def polygonFromMultipleGeometries(geometryList, useEnvelope=False, simplificationTolerance=0.0):
    polygons = [geometry.geometry for geometry in geometryList]
    return polygonFromMultiplePolygons(polygons,
                                       useEnvelope=useEnvelope,
                                       simplificationTolerance=simplificationTolerance)


def polygonFromMultiplePolygons(polygonList, useEnvelope=False, simplificationTolerance=0.0):
    polygonsToCombine = [polygon.envelope for polygon in polygonList] if useEnvelope else polygonList
    union = unary_union(polygonsToCombine)
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
    all = 3


def findCommonEdges(a, b):
    aLines = getLineListFromBoundary(a.boundary)
    edgesInCommon = []
    for aLine in aLines:
        bLines = getLineListFromBoundary(b.boundary)
        for bLine in bLines:
            edgesInCommon.append(shared_paths(aLine, bLine))
    return [edge for edge in edgesInCommon if not edge.is_empty]


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
    return findDirection(basePoint=basePoint, targetPoint=targetPoint,
                         topAngleFromCenter=topAngleFromCenterOfBaseShape)


def findDirectionOfShapeFromPoint(basePoint, targetShape):
    targetPoint = targetShape.centroid
    return findDirection(basePoint=basePoint, targetPoint=targetPoint)


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

    return degrees(sideAngle)


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


def getOppositeDirection(direction):
    if direction is CardinalDirection.north:
        return CardinalDirection.south
    elif direction is CardinalDirection.east:
        return CardinalDirection.west
    elif direction is CardinalDirection.south:
        return CardinalDirection.north
    elif direction is CardinalDirection.west:
        return CardinalDirection.east


def getCWDirection(direction):
    if direction is CardinalDirection.north:
        return CardinalDirection.east
    elif direction is CardinalDirection.east:
        return CardinalDirection.south
    elif direction is CardinalDirection.south:
        return CardinalDirection.west
    elif direction is CardinalDirection.west:
        return CardinalDirection.north


def getLineListFromBoundary(boundary):
    if isinstance(boundary, MultiLineString):
        return list(boundary.geoms)
    elif isinstance(boundary, LineString):
        return [boundary]
    return []


def shapelyGeometryToGeoJSON(geometry):
    return dumps(mapping(geometry))


def distanceBetweenGeometries(a, b):
    if isinstance(a, list):
        a = polygonFromMultipleGeometries(a)
    elif not isinstance(a, BaseGeometry):
        a = a.geometry

    if isinstance(b, list):
        b = polygonFromMultipleGeometries(b)
    elif not isinstance(b, BaseGeometry):
        b = b.geometry

    return a.distance(b)


def findClosestGeometry(originGeometry, otherGeometries):
    candidateGeometries = [block for block in otherGeometries if block is not originGeometry]
    distanceDict = {}
    for candidateGeometry in candidateGeometries:
        distance = distanceBetweenGeometries(originGeometry, candidateGeometry)
        distanceDict[distance] = candidateGeometry
    shortestDistance = min(distanceDict.keys())
    return distanceDict[shortestDistance]


def findContiguousGroupsOfGraphObjects(graphObjects):
    if graphObjects:
        remainingObjects = set(graphObjects)
        contiguousObjectGroups = []
        while remainingObjects:
            contiguousObjectGroups.append(
                forestFireFillGraphObject(candidateObjects=remainingObjects))
        return contiguousObjectGroups
    return []


def forestFireFillGraphObject(candidateObjects, startingObject=None, notInList=None):
    fireFilledObjects = []
    fireQueue = deque()
    fireQueueSet = set()
    notInSet = set(notInList) if notInList else None
    if not startingObject:
        startingObject = next(iter(candidateObjects))
    fireQueue.append(startingObject)
    fireQueueSet.add(startingObject)

    while fireQueue:
        graphObject = fireQueue.popleft()
        fireQueueSet.discard(graphObject)
        candidateObjects.discard(graphObject)
        fireFilledObjects.append(graphObject)

        for neighborObject in graphObject.allNeighbors:
            if neighborObject in candidateObjects and neighborObject not in fireQueueSet:
                if notInSet is None or neighborObject not in notInSet:
                    fireQueue.append(neighborObject)
                    fireQueueSet.add(neighborObject)

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
    _queuedSet = set()
    remainingObjects = candidateObjects.copy()
    if not startingObjects:
        # this doesn't occur during the forest fire fill when creating districts
        startingObjects = [remainingObjects[0]]
    fireQueue.append(startingObjects)
    _queuedSet.update(startingObjects)

    count = 1
    with tqdm() as pbar:
        while fireQueue:
            pbar.update(1)
            pbar.set_description(
                f'FireFilled: {len(fireFilledObjects)} - FireQueue: {len(fireQueue)} - '
                f'Remaining: {len(remainingObjects)} - Off count: {offCount}')

            # pull from the top of the queue
            graphObjectCandidateGroup = fireQueue.pop(0)
            _queuedSet.difference_update(graphObjectCandidateGroup)

            # remove objects that we pulled from the queue from the remaining list
            groupSet = set(graphObjectCandidateGroup)
            remainingObjects = [o for o in remainingObjects if o not in groupSet]

            if shouldDrawEachStep:
                plotGraphObjectGroups([fireFilledObjects, graphObjectCandidateGroup, remainingObjects],
                                      showDistrictNeighborConnections=True,
                                      saveImages=True,
                                      saveDescription=f'WeightedForestFireFillGraphObject-{id(candidateObjects)}-{count}')
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
                    # remove duplicates from a list of lists
                    groupsToRemove = [list(item) for item in set(tuple(row) for row in groupsToRemove)]
                    for groupToRemove in groupsToRemove:
                        fireQueue.remove(groupToRemove)
                        _queuedSet.difference_update(groupToRemove)
                    neighborsOfFireFilledObjects = [group.allNeighbors for group in fireFilledObjects]
                    for remainingItemFromGroups in remainingItemsFromGroups:
                        if remainingItemFromGroups in neighborsOfFireFilledObjects:
                            fireQueue.append([remainingItemFromGroups])
                            _queuedSet.add(remainingItemFromGroups)

                    # add neighbors to the queue
                    for graphObjectCandidate in graphObjectCandidateGroup:
                        for neighborObject in graphObjectCandidate.allNeighbors:
                            if neighborObject in remainingObjects and neighborObject not in _queuedSet:
                                fireQueue.append([neighborObject])
                                _queuedSet.add(neighborObject)

                    # if we don't need to return the next best candidate, we can remove groups from the queue
                    # that don't meet the condition right now to speed up processing
                    if not returnBestCandidateGroup:
                        fireQueue = [fireQueueGroup for fireQueueGroup in fireQueue if
                                     condition(fireFilledObjects, fireQueueGroup)[0]]
                        _queuedSet = {o for grp in fireQueue for o in grp}
                else:
                    if returnBestCandidateGroup and bestGraphObjectCandidateGroupThisPass is None:
                        if all([len(graphObjectCandidate.children) > 1
                                for graphObjectCandidate in graphObjectCandidateGroup]):
                            bestGraphObjectCandidateGroupThisPass = graphObjectCandidateGroup

                    remainingObjects.extend(graphObjectCandidateGroup)  # add candidate back to the queue
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
                            saveDescription=f'WeightedForestFireFillGraphObject-{id(candidateObjects)}-{count}')
                        count += 1

                    groupAndIsolatedObjects = potentiallyIsolatedObjects + graphObjectCandidateGroup

                    if groupAndIsolatedObjects not in candidateGroupsThatDidNotMeetConditionThisPass:
                        fireQueue.append(groupAndIsolatedObjects)
                        _queuedSet.update(groupAndIsolatedObjects)
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
            saveDescription=f'WeightedForestFireFillGraphObject-{id(candidateObjects)}-{count}')

    return fireFilledObjects, bestGraphObjectCandidateGroupThisPass


def combinationsFromGroup(candidateGroups, mustTouchGroup, startingGroup):
    combinations = []

    # if the group is touching a must touch object, continue, otherwise add group plus all candidates
    mustTouchGroupNeighbors = [mustTouchObjectNeighbor for mustTouchObject in mustTouchGroup for mustTouchObjectNeighbor
                               in mustTouchObject.allNeighbors]
    if any(group for group in startingGroup if group in mustTouchGroupNeighbors):

        neighborsInCandidates = [groupNeighbor for group in startingGroup for groupNeighbor in group.allNeighbors if
                                 groupNeighbor in candidateGroups]
        if neighborsInCandidates:
            for neighbor in neighborsInCandidates:
                neighborCombinations = combinationsFromGroup(
                    candidateGroups=[candidateGroup for candidateGroup in candidateGroups if
                                     candidateGroup not in startingGroup and candidateGroup is not neighbor],
                    mustTouchGroup=mustTouchGroup + startingGroup,
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


def deflatePolygonByAtMostATenth(polygon):
    def scaleBasedOnRatio(scaleRatio):
        # f(x) = (((b-a)*(x-min))/(max-min))+a
        # min = min input
        # max = max input
        # a = min output
        # b = max output
        a = 0.1
        b = 0.01
        return (((b - a) * (scaleRatio - float_info.min)) / (1 - float_info.min)) + a

    dimensions = getWidthAndHeightOfPolygonInLatLong(polygon)
    if dimensions[0] < dimensions[1]:
        shortestDimension = dimensions[0]
        ratio = dimensions[0] / dimensions[1]
    else:
        shortestDimension = dimensions[1]
        ratio = dimensions[1] / dimensions[0]
    tenthOfShortestDimension = shortestDimension * scaleBasedOnRatio(ratio)
    exteriorPolygon = Polygon(polygon.exterior)
    return exteriorPolygon.buffer(-tenthOfShortestDimension)


def isPolygonAnHourglass(polygon):
    return isinstance(deflatePolygonByAtMostATenth(polygon), MultiPolygon)


def deflationScore(polygon, shouldPlotResult=False):
    exteriorPolygon = Polygon(polygon.exterior)
    stepSize = 0.01
    count = 0
    while True:
        deflateValue = stepSize * count
        deflatedPolygon = exteriorPolygon.buffer(-deflateValue)
        if deflatedPolygon.is_empty:
            deflateValue = inf
            break
        if isinstance(deflatedPolygon, MultiPolygon):
            break
        count += 1

    if shouldPlotResult and not deflatedPolygon.is_empty:
        from exportData.displayShapes import plotPolygons
        plotPolygons([exteriorPolygon, deflatedPolygon])

    return deflateValue


def isPolygonAGoodDistrictShape(districtPolygon, parentPolygon):
    def listOfPolygons(polygon):
        polygons = list(polygon.geoms) if isinstance(polygon, MultiPolygon) else [polygon]
        return [Polygon(subPolygon.exterior) for subPolygon in polygons]

    parentPolygons = listOfPolygons(parentPolygon)
    districtPolygons = listOfPolygons(districtPolygon)

    districtPolygonsNotFullyFilled = [polygon
                                      for polygon in districtPolygons
                                      if not any(polygon == parentSubPolygon
                                                 for parentSubPolygon in parentPolygons)]
    return all(not isPolygonAnHourglass(polygon) for polygon in districtPolygonsNotFullyFilled)


def alignmentOfPolygon(polygon):
    boxDimensions = dimensionsOfPolygon(polygon)
    if boxDimensions[0] < boxDimensions[1]:
        return Alignment.northSouth
    else:
        return Alignment.westEast


def dimensionsOfPolygon(polygon):
    minLon, minLat, maxLon, maxLat = polygon.bounds
    return getWidthAndHeightOfBoxOnEarth(minLat=minLat, minLon=minLon, maxLat=maxLat, maxLon=maxLon)


def getWidthAndHeightOfBoxOnEarth(minLat, minLon, maxLat, maxLon):
    aWidth = getDistanceBetweenLatLong(lat1=minLat, lon1=minLon, lat2=minLat, lon2=maxLon)
    bWidth = getDistanceBetweenLatLong(lat1=maxLat, lon1=minLon, lat2=maxLat, lon2=maxLon)
    maxWidth = max(aWidth, bWidth)
    aHeight = getDistanceBetweenLatLong(lat1=minLat, lon1=maxLon, lat2=maxLat, lon2=maxLon)
    bHeight = getDistanceBetweenLatLong(lat1=minLat, lon1=minLon, lat2=maxLat, lon2=minLon)
    maxHeight = max(aHeight, bHeight)
    return maxWidth, maxHeight


def getWidthAndHeightOfPolygonInLatLong(polygon):
    left, bottom, right, top = polygon.bounds
    return right - left, top - bottom


def getDistanceBetweenLatLong(lat1, lon1, lat2, lon2):
    return distanceOnEarth((lat1, lon1), (lat2, lon2)).km


def polsbyPopperScoreOfPolygon(polygon):
    # score = 4 * pi * (area / perimeter^2)
    return 4 * pi * (polygon.area / (polygon.length ** 2))


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


def populationDeviationFromPercent(overallPercentage, numberOfDistricts, totalPopulation):
    idealDistrictSize = int(totalPopulation / numberOfDistricts)
    populationDeviation = int((overallPercentage * idealDistrictSize) / 2)
    return max(1, populationDeviation)
