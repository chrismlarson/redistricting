from shapely.geometry import shape
from shapely.ops import cascaded_union
from enum import Enum
from math import atan2, degrees, pi
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


def intersectingGeometries(a,b):
    return a.geometry.intersects(b.geometry)


def containingGeometries(a,b):
    aContainsBBoundary = a.geometry.boundary.within(b.geometry.boundary)
    bContainsABoundary = b.geometry.boundary.within(a.geometry.boundary)
    return aContainsBBoundary or bContainsABoundary


def isBoundaryGeometry(parent,child):
    return parent.geometry.boundary.intersects(child.geometry.boundary)


def geometryFromBlocks(blockList):
    polygons = [block.geometry for block in blockList]
    return cascaded_union(polygons)


class CardinalDirection(Enum):
    north = 1
    west = 3
    east = 0
    south = 4


def findDirection(basePoint, targetPoint):
    if basePoint == targetPoint:
        return CardinalDirection.north

    xDiff = targetPoint.x - basePoint.x
    yDiff = targetPoint.y - basePoint.y
    radianDiff = atan2(yDiff, xDiff)

    # rotate 90 degrees for easier angle matching
    radianDiff = radianDiff - (pi/2)

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