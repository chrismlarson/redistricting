from os import path
from us import states
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFile, loadDataFromFileWithDescription  # , exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, \
    prepareGraphsForAllRedistrictingGroups, RedistrictingGroup

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'Charlevoix'

censusData = loadDataFromFileWithDescription(censusYear=censusYear,
                                             stateName=stateInfo.name,
                                             descriptionOfInfo='{0}Block'.format(descriptionToWorkWith))
redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData=censusData)
# exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFile(data=AtomicBlock.atomicBlockList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='{0}AtomicBlockPreGraph'.format(descriptionToWorkWith))
saveDataToFile(data=redistrictingGroupList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(descriptionToWorkWith))

redistrictingGroupList = loadDataFromFileWithDescription(censusYear=censusYear,
                                                         stateName=stateInfo.name,
                                                         descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(
                                                             descriptionToWorkWith))
RedistrictingGroup.redistrictingGroupList = redistrictingGroupList
redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToFile(data=AtomicBlock.atomicBlockList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='{0}AtomicBlock'.format(descriptionToWorkWith))
saveDataToFile(data=redistrictingGroupList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='{0}RedistrictingGroup'.format(descriptionToWorkWith))

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))
plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroups, showPopulationCounts=True)
temp = 0
