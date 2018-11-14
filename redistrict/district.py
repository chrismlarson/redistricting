import math

from tqdm import tqdm

from exportData.displayShapes import plotDistrictCandidates, plotRedistrictingGroups, plotDistrict
from exportData.exportData import saveDataToFileWithDescription
from formatData.blockBorderGraph import BlockBorderGraph
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, geometryFromMultipleGeometries, \
    findContiguousGroupsOfGraphObjects


class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        self.removeOutdatedNeighborConnections()
        District.districtList.append(self)

    districtList = []


    def updateBlockContainerData(self):
        super(District, self).updateBlockContainerData()
        #todo: re-enable once the contiguous bug is fixed
        #validateContiguousRedistrictingGroups(self.children)


    def removeOutdatedNeighborConnections(self):
        for child in self.children:
            outdatedNeighborConnections = [neighbor for neighbor in child.allNeighbors if neighbor not in self.children]
            if outdatedNeighborConnections:
                child.removeNeighbors(outdatedNeighborConnections)

def validateContiguousRedistrictingGroups(groupList):
    contiguousRegions = findContiguousGroupsOfGraphObjects(groupList)
    if len(contiguousRegions) > 1:
        nonContiguousDistrict = [item for sublist in contiguousRegions for item in sublist]
        plotRedistrictingGroups(redistrictingGroups=nonContiguousDistrict,
                                         showDistrictNeighborConnections=True)
        raise ValueError("Don't have a contiguous set of RedictingGroups. There are {0} distinct groups".format(
            len(contiguousRegions)))


def createDistrictFromRedistrictingGroups(redistrictingGroups):
    initialDistrict = District(childrenGroups=redistrictingGroups)
    return initialDistrict


def splitDistrict(districtToSplit,
                  numberOfDistricts,
                  populationDeviation,
                  progressObject=None,
                  shouldDrawEachStep=False):
    if progressObject is None:
        tqdm.write('*** Splitting into {0} districts ***'.format(numberOfDistricts))
        progressObject = tqdm()

    districts = []

    if numberOfDistricts == 1:
        return [districtToSplit]

    aRatio = math.floor(numberOfDistricts / 2)
    bRatio = math.ceil(numberOfDistricts / 2)
    ratio = (aRatio, bRatio)

    cutDistricts = cutDistrictIntoRatio(district=districtToSplit,
                                        ratio=ratio,
                                        populationDeviation=populationDeviation,
                                        shouldDrawEachStep=shouldDrawEachStep)
    progressObject.update(1)

    # todo: remove when splits are using the breaking up logic
    if len(cutDistricts[0]) != 0:
        aDistricts = splitDistrict(District(childrenGroups=cutDistricts[0]), aRatio, populationDeviation, progressObject)
        districts.extend(aDistricts)

    if len(cutDistricts[1]) != 0:
        bDistricts = splitDistrict(District(childrenGroups=cutDistricts[1]), bRatio, populationDeviation, progressObject)
        districts.extend(bDistricts)

    return districts


def cutDistrictIntoRatio(district, ratio, populationDeviation, shouldDrawEachStep=False):
    # saveDataToFileWithDescription(data=district, descriptionOfInfo='LastDistrictForDebug', censusYear=2010, stateName='Michigan')
    # plotDistrict(district, showPopulationCounts=True, showDistrictNeighborConnections=True)
    longestDirection = alignmentOfPolygon(district.geometry)


    northernStartingCandidate = mostCardinalOfGeometries(geometryList=district.borderChildren,
                                             direction=CardinalDirection.north)
    westernStartingCandidate = mostCardinalOfGeometries(geometryList=district.borderChildren,
                                             direction=CardinalDirection.west)
    easternStartingCandidate = mostCardinalOfGeometries(geometryList=district.borderChildren,
                                             direction=CardinalDirection.east)
    southernStartingCandidate = mostCardinalOfGeometries(geometryList=district.borderChildren,
                                             direction=CardinalDirection.south)
    if longestDirection == Alignment.northSouth:
        startingGroupCandidates = (northernStartingCandidate,
                                   southernStartingCandidate,
                                   westernStartingCandidate,
                                   easternStartingCandidate)
    else:
        startingGroupCandidates = (westernStartingCandidate,
                                   easternStartingCandidate,
                                   northernStartingCandidate,
                                   southernStartingCandidate)

    ratioTotal = ratio[0] + ratio[1]
    idealDistrictASize = int(district.population / (ratioTotal / ratio[0]))
    idealDistrictBSize = int(district.population / (ratioTotal / ratio[1]))

    def withinIdealDistrictSize(currentGroups, candidateGroups):
        currentPop = sum(group.population for group in currentGroups)
        candidatePop = sum(group.population for group in candidateGroups)
        return currentPop + candidatePop <= idealDistrictASize

    def polsbyPopperScoreOfCombinedGeometry(currentGroups, remainingGroups, candidateGroups):
        geos = currentGroups + candidateGroups
        combinedShape = geometryFromMultipleGeometries(geos, useEnvelope=True) #todo: consider not using env in final
        score = polsbyPopperScoreOfPolygon(combinedShape)

        combinedRemainingShape = geometryFromMultipleGeometries(remainingGroups, useEnvelope=True)
        remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingShape)

        return score + remainingScore
    candidateDistrictA = []
    i = 0
    while not candidateDistrictA and i <= 3:
        candidateDistrictA = weightedForestFireFillGraphObject(candidateObjects=district.children,
                                                               startingObject=startingGroupCandidates[i],
                                                               condition=withinIdealDistrictSize,
                                                               weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                               shouldDrawEachStep=shouldDrawEachStep)
        i += 1
    candidateDistrictB = [group for group in district.children if group not in candidateDistrictA]

    candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
    candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

    # plotDistrictCandidates(districtCandidates=[candidateDistrictA, candidateDistrictB],
    #                        showPopulationCounts=True,
    #                        showDistrictNeighborConnections=True)

    return (candidateDistrictA, candidateDistrictB)
