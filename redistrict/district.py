import math
from tqdm import tqdm
from exportData.displayShapes import plotGraphObjectGroups, plotRedistrictingGroups, plotDistrict
from exportData.exportData import saveDataToFileWithDescription
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.redistrictingGroup import assignNeighboringRedistrictingGroupsForAllRedistrictingGroups, \
    validateContiguousRedistrictingGroups, RedistrictingGroup
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, polygonFromMultipleGeometries, \
    findContiguousGroupsOfGraphObjects, intersectingGeometries, polygonFromMultiplePolygons


class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        self.removeOutdatedNeighborConnections()
        District.districtList.append(self)

    districtList = []

    def updateBlockContainerData(self):
        super(District, self).updateBlockContainerData()
        validateContiguousRedistrictingGroups(self.children)

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
                      count=None,
                      shouldDrawFillAttempts=False,
                      shouldDrawEachStep=False):
        if count is None:
            tqdm.write('*** Splitting into {0} districts ***'.format(numberOfDistricts))
            count = 0

        districts = []

        if numberOfDistricts == 1:
            return [self]

        aRatio = math.floor(numberOfDistricts / 2)
        bRatio = math.ceil(numberOfDistricts / 2)
        ratio = (aRatio, bRatio)

        cutDistricts = self.cutDistrictIntoExactRatio(ratio=ratio,
                                                      populationDeviation=populationDeviation,
                                                      shouldDrawFillAttempts=shouldDrawFillAttempts,
                                                      shouldDrawEachStep=shouldDrawEachStep)
        count += 1
        tqdm.write('   *** Cut district into exact ratio: {0} ***'.format(count))

        aDistrict = District(childrenGroups=cutDistricts[0])
        aDistrictSplits = aDistrict.splitDistrict(numberOfDistricts=aRatio,
                                                  populationDeviation=populationDeviation,
                                                  count=count,
                                                  shouldDrawEachStep=shouldDrawEachStep)
        districts.extend(aDistrictSplits)

        bDistrict = District(childrenGroups=cutDistricts[1])
        bDistrictSplits = bDistrict.splitDistrict(numberOfDistricts=bRatio,
                                                  populationDeviation=populationDeviation,
                                                  count=count,
                                                  shouldDrawEachStep=shouldDrawEachStep)
        districts.extend(bDistrictSplits)

        return districts

    def cutDistrictIntoExactRatio(self, ratio, populationDeviation, shouldDrawFillAttempts=False, shouldDrawEachStep=False):

        ratioTotal = ratio[0] + ratio[1]
        idealDistrictASize = int(self.population / (ratioTotal / ratio[0]))
        idealDistrictBSize = int(self.population / (ratioTotal / ratio[1]))
        candidateDistrictA = []
        candidateDistrictB = []
        districtStillNotExactlyCut = True
        tqdm.write('   *** Attempting forest fire fill for a {0} to {1} ratio ***'.format(ratio[0], ratio[1]))

        count = 1
        while districtStillNotExactlyCut:
            tqdm.write('      *** Starting forest fire fill pass #{0} ***'.format(count))

            districtCandidateResult = self.cutDistrictIntoRoughRatio(idealDistrictASize=idealDistrictASize,
                                                                shouldDrawEachStep=shouldDrawEachStep)
            districtCandidates = districtCandidateResult[0]
            nextBestGroupForCandidateDistrictA = districtCandidateResult[1]

            candidateDistrictA = districtCandidates[0]
            candidateDistrictB = districtCandidates[1]

            if shouldDrawFillAttempts:
                plotGraphObjectGroups(graphObjectGroups=[candidateDistrictA, candidateDistrictB, nextBestGroupForCandidateDistrictA],
                                      showDistrictNeighborConnections=True,
                                      saveImages=True,
                                      saveDescription='DistrictSplittingIteration-{0}-{1}'.format(id(self), count))

            candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
            candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

            if idealDistrictASize - populationDeviation <= candidateDistrictAPop <= idealDistrictASize + populationDeviation and \
                    idealDistrictBSize - populationDeviation <= candidateDistrictBPop <= idealDistrictBSize + populationDeviation:
                districtStillNotExactlyCut = False
            else:
                tqdm.write('      *** Unsuccessful fill attempt. {0} off the count. ***'
                           .format(abs(idealDistrictASize - candidateDistrictAPop)))
                groupsToBreakUp = nextBestGroupForCandidateDistrictA

                tqdm.write('      *** Graph splitting {0} redistricting groups ***'.format(len(groupsToBreakUp)))
                updatedChildren = self.children.copy()
                for groupToBreakUp in groupsToBreakUp:
                    smallerRedistrictingGroups = groupToBreakUp.getGraphSplits(shouldDrawGraph=shouldDrawEachStep,
                                                                               countForProgress=groupsToBreakUp
                                                                               .index(groupToBreakUp)+1)
                    updatedChildren.extend(smallerRedistrictingGroups)
                    updatedChildren.remove(groupToBreakUp)
                    RedistrictingGroup.redistrictingGroupList.remove(groupToBreakUp)

                tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
                assignNeighboringRedistrictingGroupsForAllRedistrictingGroups()
                self.children = updatedChildren

            saveDataToFileWithDescription(data=self,
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='DistrictSplitLastIteration-{0}'.format(id(self)))
            count += 1

        return candidateDistrictA, candidateDistrictB

    def cutDistrictIntoRoughRatio(self, idealDistrictASize, shouldDrawEachStep=False):

        def withinIdealDistrictSize(currentGroups, candidateGroups):
            currentPop = sum(group.population for group in currentGroups)
            candidatePop = sum(group.population for group in candidateGroups)
            return currentPop + candidatePop <= idealDistrictASize

        def polsbyPopperScoreOfCombinedGeometry(currentGroupPolygon, remainingGroups, candidateGroups):
            # todo: consider using a low simplificationTolerance instead of envelope for greater accuracy
            candidateGroupsPolygon = polygonFromMultipleGeometries(candidateGroups,
                                                                   useEnvelope=True)
            # never useEnvelope here, because candidateGroupsPolygon is our cached shape
            candidatePolygon = polygonFromMultiplePolygons([currentGroupPolygon, candidateGroupsPolygon])
            combinedRemainingPolygon = polygonFromMultipleGeometries(remainingGroups,
                                                                     useEnvelope=True)

            score = polsbyPopperScoreOfPolygon(candidatePolygon)
            remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingPolygon)

            return score + remainingScore

        candidateDistrictA = []

        startingGroupCandidates = self.getCutStartingCandidates()

        nextBestGroupFromCandidateDistrictA = None
        i = 0
        while not candidateDistrictA and i <= 3:
            candidateDistrictAResult = weightedForestFireFillGraphObject(candidateObjects=self.children,
                                                                   startingObjects=[startingGroupCandidates[i]],
                                                                   condition=withinIdealDistrictSize,
                                                                   weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                                   shouldDrawEachStep=shouldDrawEachStep)
            candidateDistrictA = candidateDistrictAResult[0]
            nextBestGroupFromCandidateDistrictA = candidateDistrictAResult[1]
            i += 1
        candidateDistrictB = [group for group in self.children if group not in candidateDistrictA]

        return (candidateDistrictA, candidateDistrictB), nextBestGroupFromCandidateDistrictA


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
