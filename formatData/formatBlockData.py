from os import path
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFile, loadDataFromFile#, exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, prepareGraphsForAllRedistrictingGroups


blockFilePath = path.expanduser('~/Documents/2010-Michigan-AllBlocksInfo.redistdata')
redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(filePath=blockFilePath)
#exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFile(data=AtomicBlock.atomicBlockList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='AllAtomicBlocksPreGraph')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='AllRedistrictingGroupsPreGraph')
redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToFile(data=AtomicBlock.atomicBlockList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='AllAtomicBlocks')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='AllRedistrictingGroups')


# redistGroupsFilePath = path.expanduser('~/Documents/2010-Michigan-AllAtomicBlocksInfo.redistdata')
# redistrictingGroups = loadDataFromFile(filePath=redistGroupsFilePath)
# plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroups)
# temp =0