from os import path
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFile, loadDataFromFile#, exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, \
    prepareGraphsForAllRedistrictingGroups, RedistrictingGroup

# blockFilePath = path.expanduser('~/Documents/2010-Michigan-KeweenawAndMackinacBlockInfo.redistdata')
#
# redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(filePath=blockFilePath)
# #exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
# saveDataToFile(data=AtomicBlock.atomicBlockList, censusYear='2010', stateName='Michigan',
#                descriptionOfInfo='KeweenawAndMackinacAtomicBlocksPreGraph')
# saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
#                descriptionOfInfo='KeweenawAndMackinacRedistrictingGroupsPreGraph')


redistGroupsFilePath = path.expanduser('~/Documents/2010-Michigan-KeweenawAndMackinacRedistrictingGroupsPreGraphInfo.redistdata')
RedistrictingGroup.redistrictingGroupList = loadDataFromFile(filePath=redistGroupsFilePath)
redistrictingGroupList = prepareGraphsForAllRedistrictingGroups()
saveDataToFile(data=AtomicBlock.atomicBlockList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='KeweenawAndMackinacAtomicBlocks')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='KeweenawAndMackinacRedistrictingGroups')


redistGroupsFilePath = path.expanduser('~/Documents/2010-Michigan-KeweenawAndMackinacRedistrictingGroupsInfo.redistdata')
redistrictingGroups = loadDataFromFile(filePath=redistGroupsFilePath)
plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroups, showPopulationCounts=True)
temp =0