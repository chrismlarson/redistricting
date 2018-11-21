from os import path

from us import states
from exportData.displayShapes import plotDistricts
from exportData.exportData import loadDataFromFileWithDescription, saveDataToFileWithDescription, loadDataFromFile
from redistrict.district import createDistrictFromRedistrictingGroups

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

# filePath = path.expanduser('~/Documents/--DistrictSplittingIteration1Info.redistdata')
# initialDistrict = loadDataFromFile(filePath)
#
# for redistrictingGroup in initialDistrict.children:
#     if redistrictingGroup.graphId == 330036:
#         redistrictingGroup.getGraphSplits(shouldDrawGraph=True)


redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))

initialDistrict = createDistrictFromRedistrictingGroups(redistrictingGroups=redistrictingGroups)

districts = initialDistrict.splitDistrict(numberOfDistricts=14,
                                          populationDeviation=1,
                                          shouldDrawFillAttempts=True)
plotDistricts(districts=districts,
              showPopulationCounts=True,
              showDistrictNeighborConnections=True)
saveDataToFileWithDescription(data=districts,
                              censusYear=censusYear,
                              stateName=stateInfo,
                              descriptionOfInfo='{0}-InitialDistrictSplitExactly'.format(descriptionToWorkWith))
temp = 0
