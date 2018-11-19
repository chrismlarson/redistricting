import math

from tqdm import tqdm

from exportData.displayShapes import plotGraphObjectGroups, plotRedistrictingGroups, plotDistrict
from exportData.exportData import saveDataToFileWithDescription
from formatData.blockBorderGraph import BlockBorderGraph
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, geometryFromMultipleGeometries, \
    findContiguousGroupsOfGraphObjects, intersectingGeometries


class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        self.removeOutdatedNeighborConnections()
        District.districtList.append(self)

    districtList = []

    def updateBlockContainerData(self):
        super(District, self).updateBlockContainerData()
        # todo: re-enable once the contiguous bug is fixed
        # validateContiguousRedistrictingGroups(self.children)

    def removeOutdatedNeighborConnections(self):
        for child in self.children:
            outdatedNeighborConnections = [neighbor for neighbor in child.allNeighbors if neighbor not in self.children]
            if outdatedNeighborConnections:
                child.removeNeighbors(outdatedNeighborConnections)

    def getCutStartingCandidates(self):
        longestDirection = alignmentOfPolygon(self.geometry)

        northernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                             direction=CardinalDirection.north)
        westernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                            direction=CardinalDirection.west)
        easternStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                            direction=CardinalDirection.east)
        southernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
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

        return startingGroupCandidates

    def splitDistrict(self,
                      numberOfDistricts,
                      populationDeviation,
                      progressObject=None,
                      shouldDrawEachStep=False):
        if progressObject is None:
            tqdm.write('*** Splitting into {0} districts ***'.format(numberOfDistricts))
            progressObject = tqdm()

        districts = []

        if numberOfDistricts == 1:
            return [self]

        aRatio = math.floor(numberOfDistricts / 2)
        bRatio = math.ceil(numberOfDistricts / 2)
        ratio = (aRatio, bRatio)

        cutDistricts = self.cutDistrictIntoExactRatio(ratio=ratio,
                                                      populationDeviation=populationDeviation,
                                                      shouldDrawEachStep=shouldDrawEachStep)
        progressObject.update(1)

        aDistrict = District(childrenGroups=cutDistricts[0])
        aDistrictSplits = aDistrict.splitDistrict(numberOfDistricts=aRatio,
                                                  populationDeviation=populationDeviation,
                                                  progressObject=progressObject,
                                                  shouldDrawEachStep=shouldDrawEachStep)
        districts.extend(aDistrictSplits)

        bDistrict = District(childrenGroups=cutDistricts[1])
        bDistrictSplits = bDistrict.splitDistrict(numberOfDistricts=bRatio,
                                                  populationDeviation=populationDeviation,
                                                  progressObject=progressObject,
                                                  shouldDrawEachStep=shouldDrawEachStep)
        districts.extend(bDistrictSplits)

        return districts

    def cutDistrictIntoExactRatio(self, ratio, populationDeviation, shouldDrawEachStep=False):

        ratioTotal = ratio[0] + ratio[1]
        idealDistrictASize = int(self.population / (ratioTotal / ratio[0]))
        idealDistrictBSize = int(self.population / (ratioTotal / ratio[1]))
        candidateDistrictA = []
        candidateDistrictB = []
        districtStillNotExactlyCut = True
        tqdm.write('*** Attempting forest fire fill for a {0} to {1} ratio ***'.format(ratio[0], ratio[1]))

        while districtStillNotExactlyCut:

            districtCandidates = self.cutDistrictIntoRoughRatio(idealDistrictASize=idealDistrictASize,
                                                                shouldDrawEachStep=shouldDrawEachStep)
            candidateDistrictA = districtCandidates[0]
            candidateDistrictB = districtCandidates[1]

            candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
            candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

            if idealDistrictASize - populationDeviation <= candidateDistrictAPop <= idealDistrictASize + populationDeviation and \
               idealDistrictBSize - populationDeviation <= candidateDistrictBPop <= idealDistrictBSize + populationDeviation:
                districtStillNotExactlyCut = False
            else:
                tqdm.write('   *** Unsuccessful fill attempt. {0} off the count. ***'
                    .format(abs(idealDistrictASize - candidateDistrictAPop)))
                groupsToBreakUp = getRedistrictingGroupsBetweenCandidates(aCandidate=candidateDistrictA,
                                                                          bCandidate=candidateDistrictB)

                tqdm.write('   *** Graph splitting {0} redistricting groups ***'.format(len(groupsToBreakUp)))
                updatedChildren = self.children.copy()
                for groupToBreakUp in groupsToBreakUp:
                    smallerRedistrictingGroups = groupToBreakUp.getGraphSplits(shouldDrawGraph=True)
                    updatedChildren.extend(smallerRedistrictingGroups)
                    updatedChildren.remove(groupToBreakUp)
                self.children = updatedChildren

        return (candidateDistrictA, candidateDistrictB)

    def cutDistrictIntoRoughRatio(self, idealDistrictASize, shouldDrawEachStep=False):

        def withinIdealDistrictSize(currentGroups, candidateGroups):
            currentPop = sum(group.population for group in currentGroups)
            candidatePop = sum(group.population for group in candidateGroups)
            return currentPop + candidatePop <= idealDistrictASize

        def polsbyPopperScoreOfCombinedGeometry(currentGroups, remainingGroups, candidateGroups):
            geos = currentGroups + candidateGroups
            combinedShape = geometryFromMultipleGeometries(geos,
                                                           useEnvelope=True)  # todo: consider not using env in final
            score = polsbyPopperScoreOfPolygon(combinedShape)

            combinedRemainingShape = geometryFromMultipleGeometries(remainingGroups, useEnvelope=True)
            remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingShape)

            return score + remainingScore

        candidateDistrictA = []

        startingGroupCandidates = self.getCutStartingCandidates()

        i = 0
        while not candidateDistrictA and i <= 3:
            candidateDistrictA = weightedForestFireFillGraphObject(candidateObjects=self.children,
                                                                   startingObject=startingGroupCandidates[i],
                                                                   condition=withinIdealDistrictSize,
                                                                   weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                                   shouldDrawEachStep=shouldDrawEachStep)
            i += 1
        candidateDistrictB = [group for group in self.children if group not in candidateDistrictA]

        return (candidateDistrictA, candidateDistrictB)


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


def getRedistrictingGroupsBetweenCandidates(aCandidate, bCandidate):
    groupsBetween = []

    for aGroup in aCandidate:
        for bGroup in bCandidate:
            if intersectingGeometries(aGroup, bGroup):
                if aGroup not in groupsBetween:
                    groupsBetween.append(aGroup)
                if bGroup not in groupsBetween:
                    groupsBetween.append(bGroup)

    return groupsBetween