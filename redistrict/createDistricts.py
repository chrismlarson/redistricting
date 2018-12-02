from os import path
from us import states
from exportData.displayShapes import plotDistricts
from exportData.exportData import loadDataFromFileWithDescription, saveDataToFileWithDescription, loadDataFromFile
from redistrict.district import createDistrictFromRedistrictingGroups

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

# filePath = path.expanduser('~/Documents/--DistrictSplitLastIteration-1420308615120Info.redistdata')
# initialDistrict = loadDataFromFile(filePath)
#
# for child in initialDistrict.children:
#     if child.graphId == 330019:
#         saveDataToFileWithDescription(data=child,
#                                       censusYear='',
#                                       stateName='',
#                                       descriptionOfInfo='RedistrictingGroup-CouldNotFindSplit')

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))

initialDistrict = createDistrictFromRedistrictingGroups(redistrictingGroups=redistrictingGroups)

districts = initialDistrict.splitDistrict(numberOfDistricts=14,
                                          populationDeviation=1,
                                          shouldDrawFillAttempts=False,
                                          splitBestCandidateGroup=True)
saveDataToFileWithDescription(data=districts,
                              censusYear=censusYear,
                              stateName=stateInfo,
                              descriptionOfInfo='{0}-InitialDistrictSplitExactly'.format(descriptionToWorkWith))
plotDistricts(districts=districts,
              showPopulationCounts=True,
              showDistrictNeighborConnections=True)
temp = 0
