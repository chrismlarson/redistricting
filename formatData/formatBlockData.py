from us import states
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFileWithDescription, loadDataFromFileWithDescription, \
    loadDataFromDirectoryWithDescription, saveDataToDirectoryWithDescription  # , exportGeographiesToShapefile
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, \
    prepareGraphsForAllRedistrictingGroups, RedistrictingGroup, prepareBlockGraphsForAllRedistrictingGroups

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

censusData = loadDataFromFileWithDescription(censusYear=censusYear,
                                             stateName=stateInfo.name,
                                             descriptionOfInfo='{0}Block'.format(descriptionToWorkWith))
RedistrictingGroup.redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(
    censusData=censusData)
# exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFileWithDescription(data=RedistrictingGroup.redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(descriptionToWorkWith))

RedistrictingGroup.redistrictingGroupList = prepareBlockGraphsForAllRedistrictingGroups()
saveDataToFileWithDescription(data=RedistrictingGroup.redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroupBlockGraphsPrepared'
                              .format(descriptionToWorkWith))

RedistrictingGroup.redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToFileWithDescription(data=RedistrictingGroup.redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroup'.format(descriptionToWorkWith))
plotBlocksForRedistrictingGroups(redistrictingGroups=RedistrictingGroup.redistrictingGroupList,
                                 showDistrictNeighborConnections=True)
