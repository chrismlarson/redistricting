from us import states
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFileWithDescription, loadDataFromFileWithDescription, \
    loadDataFromDirectoryWithDescription, saveDataToDirectoryWithDescription  # , exportGeographiesToShapefile
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, \
    prepareGraphsForAllRedistrictingGroups, RedistrictingGroup

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

censusData = loadDataFromFileWithDescription(censusYear=censusYear,
                                             stateName=stateInfo.name,
                                             descriptionOfInfo='{0}Block'.format(descriptionToWorkWith))
redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData=censusData)
# exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToDirectoryWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(descriptionToWorkWith))

redistrictingGroupList = loadDataFromDirectoryWithDescription(censusYear=censusYear,
                                                              stateName=stateInfo.name,
                                                              descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(
                                                                  descriptionToWorkWith))

RedistrictingGroup.redistrictingGroupList = redistrictingGroupList
redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToDirectoryWithDescription(data=redistrictingGroupList,
                                   censusYear=censusYear,
                                   stateName=stateInfo.name,
                                   descriptionOfInfo='{0}RedistrictingGroupReady'.format(descriptionToWorkWith))
saveDataToFileWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroup'.format(descriptionToWorkWith))

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))
plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroups, showDistrictNeighborConnections=True)
