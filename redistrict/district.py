import math
from exportData.displayShapes import plotDistrictCandidates
from formatData.blockBorderGraph import BlockBorderGraph
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, geometryFromMultipleGeometries


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
    ratio = (aRatio, bRatio)
    cutDistricts = cutDistrictIntoRatio(districtToSplit, ratio, populationDeviation)

    aDistricts = splitDistrict(cutDistricts[0], aRatio, populationDeviation)
    bDistricts = splitDistrict(cutDistricts[1], bRatio, populationDeviation)

    districts.extend(aDistricts)
    districts.extend(bDistricts)

    return districts


def cutDistrictIntoRatio(district, ratio, populationDeviation):
    longestDirection = alignmentOfPolygon(district.geometry)

    if longestDirection == Alignment.northSouth:
        startingGroup = mostCardinalOfGeometries(geometryList=district.borderChildren,
                                                 direction=CardinalDirection.north)
    else:
        startingGroup = mostCardinalOfGeometries(geometryList=district.borderChildren, direction=CardinalDirection.west)

    ratioTotal = ratio[0] + ratio[1]
    idealDistrictASize = int(district.population / (ratioTotal / ratio[0]))
    idealDistrictBSize = int(district.population / (ratioTotal / ratio[1]))

    def withinIdealDistrictSize(currentGroups, candidateGroup):
        currentPop = sum(group.population for group in currentGroups)
        return currentPop + candidateGroup.population <= idealDistrictASize

    def polsbyPopperScoreOfCombinedGeometry(currentGroups, candidateGroup):
        geos = currentGroups + [candidateGroup]
        combinedShape = geometryFromMultipleGeometries(geos)
        score = polsbyPopperScoreOfPolygon(combinedShape)
        return score

    candidateDistrictA = weightedForestFireFillGraphObject(candidateObjects=district.children,
                                                           startingObject=startingGroup,
                                                           condition=withinIdealDistrictSize,
                                                           weightingScore=polsbyPopperScoreOfCombinedGeometry)
    candidateDistrictB = [group for group in district.children if group not in candidateDistrictA]

    candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
    candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

    plotDistrictCandidates(districtCandidates=[candidateDistrictA, candidateDistrictB],
                           showPopulationCounts=True,
                           showDistrictNeighborConnections=True)

    raise NotImplementedError('cutDistrictIntoRatio')
