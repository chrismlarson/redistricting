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

# censusData = loadDataFromFileWithDescription(censusYear=censusYear,
#                                              stateName=stateInfo.name,
#                                              descriptionOfInfo='KeweenawAndTheThumbBlock')
# redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData=censusData)
# # exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
# saveDataToFile(data=AtomicBlock.atomicBlockList,
#                censusYear=censusYear,
#                stateName=stateInfo.name,
#                descriptionOfInfo='KeweenawAndTheThumbAtomicBlockPreGraph')
# saveDataToFile(data=redistrictingGroupList,
#                censusYear=censusYear,
#                stateName=stateInfo.name,
#                descriptionOfInfo='KeweenawAndTheThumbRedistrictingGroupPreGraph')

redistrictingGroupList = loadDataFromFileWithDescription(censusYear=censusYear,
                                                         stateName=stateInfo.name,
                                                         descriptionOfInfo='KeweenawAndTheThumbRedistrictingGroupPreGraph')
RedistrictingGroup.redistrictingGroupList = redistrictingGroupList
redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToFile(data=AtomicBlock.atomicBlockList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='KeweenawAndTheThumbAtomicBlock')
saveDataToFile(data=redistrictingGroupList,
               censusYear=censusYear,
               stateName=stateInfo.name,
               descriptionOfInfo='KeweenawAndTheThumbRedistrictingGroup')

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='KeweenawAndTheThumbRedistrictingGroup')
plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroups, showPopulationCounts=True)
temp = 0
