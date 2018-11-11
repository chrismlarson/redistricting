import math
from exportData.displayShapes import plotDistrictCandidates
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

    def removeOutdatedNeighborConnections(self):
        for child in self.children:
            outdatedNeighborConnections = [neighbor for neighbor in child.allNeighbors if neighbor not in self.children]
            if outdatedNeighborConnections:
                child.removeNeighbors(outdatedNeighborConnections)


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

    aDistricts = splitDistrict(District(childrenGroups=cutDistricts[0]), aRatio, populationDeviation)
    bDistricts = splitDistrict(District(childrenGroups=cutDistricts[1]), bRatio, populationDeviation)

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

    def polsbyPopperScoreOfCombinedGeometry(currentGroups, remainingGroups, candidateGroup):
        geos = currentGroups + [candidateGroup]
        combinedShape = geometryFromMultipleGeometries(geos, useEnvelope=True) #todo: consider not using env in final
        score = polsbyPopperScoreOfPolygon(combinedShape)

        combinedRemainingShape = geometryFromMultipleGeometries(remainingGroups, useEnvelope=True)
        remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingShape)

        return score + remainingScore

    def contiguousGroupsInReminaingGroups(remainingGroups, ignoredGroups, currentGroups, queuedGroups, candidateGroup):
        contiguousGroups = findContiguousGroupsOfGraphObjects(graphObjects=remainingGroups + ignoredGroups)
        # todo: there might be something wrong when len(contiguousGroups) == 0
        if len(contiguousGroups) <= 1: #candidate won't block any other groups
            return (False, None)
        else:
            #check to see if all neighbors of candidate block will still fit in district
            candidateNeighbors = [neighbor for neighbor in candidateGroup.borderChildren
                                  if neighbor in remainingGroups + ignoredGroups]
            neighborPop = sum(group.population for group in candidateNeighbors)

            #find the contiguous group with the largest population and remove it from population calculations
            contiguousGroups.sort(key=lambda x: sum(group.population for group in x), reverse=True)
            contiguousGroups.remove(contiguousGroups[0])
            isolatedGroups = [group
                              for groupList in contiguousGroups
                              for group in groupList]
            isolatedGroupsPop = sum(group.population for group in isolatedGroups)

            currentPop = sum(group.population for group in currentGroups)
            potentialPop = currentPop + neighborPop + isolatedGroupsPop

            if potentialPop <= idealDistrictASize:
                return (False, isolatedGroups)
            else:
                return (True, None)

    candidateDistrictA = weightedForestFireFillGraphObject(candidateObjects=district.children,
                                                           startingObject=startingGroup,
                                                           condition=withinIdealDistrictSize,
                                                           weightingScore=polsbyPopperScoreOfCombinedGeometry,
                                                           ignoreCondition=contiguousGroupsInReminaingGroups)
    candidateDistrictB = [group for group in district.children if group not in candidateDistrictA]

    candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
    candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

    plotDistrictCandidates(districtCandidates=[candidateDistrictA, candidateDistrictB],
                           showPopulationCounts=True,
                           showDistrictNeighborConnections=True)

    return (candidateDistrictA, candidateDistrictB)
