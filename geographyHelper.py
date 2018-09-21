from shapely.geometry import shape
from shapely.ops import cascaded_union
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
