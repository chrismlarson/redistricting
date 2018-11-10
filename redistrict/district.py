import math

from exportData.displayShapes import plotRedistrictingGroups
from formatData.blockBorderGraph import BlockBorderGraph
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection


class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        District.districtList.append(self)

    districtList = []


def createDistrictFromRedistrictingGroups(redistrictingGroups):
    initialDistrict = District(childrenGroups=redistrictingGroups)
    return initialDistrict


def splitDistrict(districtToSplit, numberOfDistricts, populationDeviation):
    districts = []

    if numberOfDistricts == 1:
        return districtToSplit

    aRatio = math.floor(numberOfDistricts / 2)
    bRatio = math.ceil(numberOfDistricts / 2)
    cutDistricts = cutDistrictIntoRatio(districtToSplit, aRatio, bRatio, populationDeviation)

    aDistricts = splitDistrict(cutDistricts[0], aRatio, populationDeviation)
    bDistricts = splitDistrict(cutDistricts[1], bRatio, populationDeviation)

    districts.extend(aDistricts)
    districts.extend(bDistricts)

    return districts


def cutDistrictIntoRatio(district, aRatio, bRatio, populationDeviation):
    longestDirection = alignmentOfPolygon(district.geometry)

    if longestDirection == Alignment.northSouth:
        startingGroup = mostCardinalOfGeometries(geometryList=district.borderChildren, direction=CardinalDirection.north)
    else:
        startingGroup = mostCardinalOfGeometries(geometryList=district.borderChildren, direction=CardinalDirection.west)

    plotRedistrictingGroups(redistrictingGroups=[startingGroup], showDistrictNeighborConnections=True)

    idealDistrictASize = int(district.population / aRatio)
    idealDistrictBSize = int(district.population / bRatio)
    # while not all([math.isclose(district.population, idealDistrictASize, abs_tol=populationDeviation)
    #                for district in districts]):
    #     temp = 0
    raise NotImplementedError('cutDistrictIntoRatio')
