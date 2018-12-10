import math
from tqdm import tqdm
from exportData.displayShapes import plotGraphObjectGroups
from exportData.exportData import saveDataToFileWithDescription
from formatData.atomicBlock import assignNeighborBlocksFromCandidateBlocks
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.redistrictingGroup import validateContiguousRedistrictingGroups, RedistrictingGroup, \
    assignNeighboringRedistrictingGroupsToRedistrictingGroups, validateRedistrictingGroups
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, polygonFromMultipleGeometries, \
    intersectingGeometries, polygonFromMultiplePolygons, findContiguousGroupsOfGraphObjects


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
                      shouldMergeIntoFormerRedistrictingGroups=False,
                      shouldDrawFillAttempts=False,
                      shouldDrawEachStep=False,
                      splitBestCandidateGroup=False,
                      fastCalculations=True,
                      showDetailedProgress=False):
        if count is None:
            tqdm.write('*** Splitting into {0} districts ***'.format(numberOfDistricts))
            count = 0

        districts = []

        if numberOfDistricts == 1:
            return [self]

        aRatio = math.floor(numberOfDistricts / 2)
        bRatio = math.ceil(numberOfDistricts / 2)
        ratio = (aRatio, bRatio)

        cutDistrict = self.cutDistrictIntoExactRatio(ratio=ratio,
                                                     populationDeviation=populationDeviation,
                                                     shouldDrawFillAttempts=shouldDrawFillAttempts,
                                                     shouldDrawEachStep=shouldDrawEachStep,
                                                     shouldMergeIntoFormerRedistrictingGroups=shouldMergeIntoFormerRedistrictingGroups,
                                                     splitBestCandidateGroup=splitBestCandidateGroup,
                                                     fastCalculations=fastCalculations,
                                                     showDetailedProgress=showDetailedProgress)
        count += 1
        tqdm.write('   *** Cut district into exact ratio: {0} ***'.format(count))

        aDistrict = District(childrenGroups=cutDistrict[0])
        aDistrictSplits = aDistrict.splitDistrict(numberOfDistricts=aRatio,
                                                  populationDeviation=populationDeviation,
                                                  count=count,
                                                  shouldDrawEachStep=shouldDrawEachStep,
                                                  splitBestCandidateGroup=splitBestCandidateGroup)
        districts.extend(aDistrictSplits)

        bDistrict = District(childrenGroups=cutDistrict[1])
        bDistrictSplits = bDistrict.splitDistrict(numberOfDistricts=bRatio,
                                                  populationDeviation=populationDeviation,
                                                  count=count,
                                                  shouldDrawEachStep=shouldDrawEachStep,
                                                  splitBestCandidateGroup=splitBestCandidateGroup)
        districts.extend(bDistrictSplits)

        return districts

    def cutDistrictIntoExactRatio(self, ratio, populationDeviation, shouldDrawFillAttempts=False,
                                  shouldDrawEachStep=False, shouldMergeIntoFormerRedistrictingGroups=False,
                                  splitBestCandidateGroup=False, fastCalculations=True, showDetailedProgress=False):

        ratioTotal = ratio[0] + ratio[1]
        idealDistrictASize = int(self.population / (ratioTotal / ratio[0]))
        idealDistrictBSize = int(self.population / (ratioTotal / ratio[1]))
        candidateDistrictA = []
        candidateDistrictB = []
        districtStillNotExactlyCut = True
        tqdm.write(
            '   *** Attempting forest fire fill for a {0} to {1} ratio on: ***'.format(ratio[0], ratio[1], id(self)))

        count = 1
        while districtStillNotExactlyCut:
            tqdm.write('      *** Starting forest fire fill pass #{0} ***'.format(count))

            if len(candidateDistrictA) == 0:
                districtAStartingGroup = None
            else:
                districtAStartingGroup = candidateDistrictA
            districtCandidateResult = self.cutDistrictIntoRoughRatio(idealDistrictASize=idealDistrictASize,
                                                                     districtAStartingGroup=districtAStartingGroup,
                                                                     shouldDrawEachStep=shouldDrawEachStep,
                                                                     returnBestCandidateGroup=splitBestCandidateGroup,
                                                                     fastCalculations=fastCalculations)
            districtCandidates = districtCandidateResult[0]
            nextBestGroupForCandidateDistrictA = districtCandidateResult[1]

            candidateDistrictA = districtCandidates[0]
            candidateDistrictB = districtCandidates[1]

            if shouldDrawFillAttempts:
                if nextBestGroupForCandidateDistrictA is None:
                    nextBestGroupForCandidateDistrictA = []
                plotGraphObjectGroups(
                    graphObjectGroups=[candidateDistrictA, candidateDistrictB, nextBestGroupForCandidateDistrictA],
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
                if splitBestCandidateGroup:
                    groupsToBreakUp = nextBestGroupForCandidateDistrictA
                else:
                    groupsBetweenCandidates = getRedistrictingGroupsBetweenCandidates(candidateDistrictA,
                                                                                      candidateDistrictB)
                    groupsToBreakUp = [groupToBreakUp for groupToBreakUp in groupsBetweenCandidates
                                       if groupToBreakUp not in candidateDistrictA]

                groupsCapableOfBreaking = [groupToBreakUp for groupToBreakUp in groupsToBreakUp
                                           if len(groupToBreakUp.children) > 1]
                if len(groupsCapableOfBreaking) == 0:
                    raise RuntimeError("Groups to break up don't meet criteria. Groups: {0}".format(
                        [groupToBreakUp.graphId for groupToBreakUp in groupsToBreakUp]
                    ))

                tqdm.write(
                    '      *** Graph splitting {0} redistricting groups ***'.format(len(groupsCapableOfBreaking)))
                updatedChildren = self.children.copy()
                newRedistrictingGroups = []
                if showDetailedProgress:
                    pbar = None
                else:
                    pbar = tqdm(total=len(groupsCapableOfBreaking))
                for groupToBreakUp in groupsCapableOfBreaking:
                    if showDetailedProgress:
                        countForProgress = groupsCapableOfBreaking.index(groupToBreakUp) + 1
                    else:
                        countForProgress = None
                    smallerRedistrictingGroups = groupToBreakUp.getGraphSplits(shouldDrawGraph=shouldDrawEachStep,
                                                                               countForProgress=countForProgress)
                    updatedChildren.extend(smallerRedistrictingGroups)
                    updatedChildren.remove(groupToBreakUp)
                    RedistrictingGroup.redistrictingGroupList.remove(groupToBreakUp)

                    # assign the previous parent graphId so that we can combine the parts again after the exact split
                    for smallerRedistrictingGroup in smallerRedistrictingGroups:
                        if groupToBreakUp.previousParentId is None:
                            previousParentId = groupToBreakUp.graphId
                        else:
                            previousParentId = groupToBreakUp.previousParentId
                        smallerRedistrictingGroup.previousParentId = previousParentId

                    newRedistrictingGroups.extend(smallerRedistrictingGroups)
                    if pbar is not None:
                        pbar.update(1)
                if pbar is not None:
                    pbar.close()

                tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
                assignNeighboringRedistrictingGroupsToRedistrictingGroups(
                    changedRedistrictingGroups=newRedistrictingGroups,
                    allNeighborCandidates=updatedChildren)
                validateRedistrictingGroups(updatedChildren)

                tqdm.write('      *** Updating District Candidate Data ***')
                self.children = updatedChildren

            saveDataToFileWithDescription(data=(self, candidateDistrictA, ratio),
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='DistrictSplitLastIteration-{0}'.format(id(self)))
            count += 1

        if shouldMergeIntoFormerRedistrictingGroups:
            # todo: remove the saves after debugged tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
            saveDataToFileWithDescription(data=[candidateDistrictA, candidateDistrictB],
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='PreMergedCandidates')
            mergedCandidates = mergeCandidatesIntoPreviousGroups(
                candidates=[candidateDistrictA, candidateDistrictB])
            candidateDistrictA = mergedCandidates[0]
            candidateDistrictB = mergedCandidates[1]
            saveDataToFileWithDescription(data=[candidateDistrictA, candidateDistrictB],
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='PostMergedCandidates')

        tqdm.write('   *** Sucessful fill attempt!!! *** <------------------------------------------------------------')
        return candidateDistrictA, candidateDistrictB

    def cutDistrictIntoRoughRatio(self, idealDistrictASize, districtAStartingGroup=None, shouldDrawEachStep=False,
                                  returnBestCandidateGroup=False, fastCalculations=True):

        def withinIdealDistrictSize(currentGroups, candidateGroups):
            currentPop = sum(group.population for group in currentGroups)
            candidatePop = sum(group.population for group in candidateGroups)
            proposedPop = currentPop + candidatePop
            isWithinIdealPop = proposedPop <= idealDistrictASize
            proposedPopDiff = idealDistrictASize - proposedPop
            return isWithinIdealPop, proposedPopDiff

        def polsbyPopperScoreOfCombinedGeometry(currentGroupPolygon, remainingGroups, candidateGroups,
                                                fastCalculations=True):
            candidateGroupsPolygon = polygonFromMultipleGeometries(candidateGroups,
                                                                   useEnvelope=fastCalculations)
            # never useEnvelope here, because candidateGroupsPolygon is our cached shape
            candidatePolygon = polygonFromMultiplePolygons([currentGroupPolygon, candidateGroupsPolygon])
            combinedRemainingPolygon = polygonFromMultipleGeometries(remainingGroups,
                                                                     useEnvelope=fastCalculations)

            score = polsbyPopperScoreOfPolygon(candidatePolygon)
            remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingPolygon)

            return score + remainingScore

        candidateDistrictA = []
        nextBestGroupFromCandidateDistrictA = None

        if districtAStartingGroup:
            candidateDistrictAResult = weightedForestFireFillGraphObject(candidateObjects=self.children,
                                                                         startingObjects=districtAStartingGroup,
                                                                         condition=withinIdealDistrictSize,
                                                                         weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                                         shouldDrawEachStep=shouldDrawEachStep,
                                                                         returnBestCandidateGroup=returnBestCandidateGroup,
                                                                         fastCalculations=fastCalculations)
            candidateDistrictA = candidateDistrictAResult[0]
            nextBestGroupFromCandidateDistrictA = candidateDistrictAResult[1]
        else:
            startingGroupCandidates = self.getCutStartingCandidates()
            i = 0
            while not candidateDistrictA and i <= 3:
                candidateDistrictAResult = weightedForestFireFillGraphObject(candidateObjects=self.children,
                                                                             startingObjects=[
                                                                                 startingGroupCandidates[i]],
                                                                             condition=withinIdealDistrictSize,
                                                                             weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                                             shouldDrawEachStep=shouldDrawEachStep,
                                                                             returnBestCandidateGroup=returnBestCandidateGroup,
                                                                             fastCalculations=fastCalculations)
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


def mergeCandidatesIntoPreviousGroups(candidates):
    mergedCandidates = []
    for candidate in candidates:

        # group redistricting groups together based on previous parent
        parentDict = {}
        for redistrictingGroup in candidate:
            # if it doesn't have a previous parent, that means it wasn't broken up, so we will just let is pass through
            if redistrictingGroup.previousParentId is None:
                parentDict[redistrictingGroup.graphId] = [redistrictingGroup]
            else:
                if redistrictingGroup.previousParentId in parentDict:
                    parentDict[redistrictingGroup.previousParentId].append(redistrictingGroup)
                else:
                    parentDict[redistrictingGroup.previousParentId] = [redistrictingGroup]

        # merge the grouped groups together
        mergedRedistrictingGroups = []
        with tqdm(total=len(parentDict)) as pbar:
            for redistrictingGroupList in parentDict.values():
                if len(redistrictingGroupList) == 1:
                    mergedRedistrictingGroups.append(redistrictingGroupList[0])
                else:
                    allBorderBlocks = []
                    allBlocks = []
                    for redistrictingGroup in redistrictingGroupList:
                        allBorderBlocks.extend(redistrictingGroup.borderChildren)
                        allBlocks.extend(redistrictingGroup.children)

                    # assign block neighbors to former border blocks
                    for formerBorderBlock in allBorderBlocks:
                        assignNeighborBlocksFromCandidateBlocks(block=formerBorderBlock,
                                                                candidateBlocks=allBorderBlocks)

                    contiguousRegions = findContiguousGroupsOfGraphObjects(allBlocks)

                    mergedRedistrictingGroupsForPrevious = []
                    for contiguousRegion in contiguousRegions:
                        contiguousRegionGroup = RedistrictingGroup(childrenBlocks=contiguousRegion)
                        contiguousRegionGroup.validateBlockNeighbors()
                        mergedRedistrictingGroupsForPrevious.append(contiguousRegionGroup)
                    mergedRedistrictingGroups.extend(mergedRedistrictingGroupsForPrevious)
                pbar.update(1)

        mergedCandidates.append(mergedRedistrictingGroups)

    return mergedCandidates
