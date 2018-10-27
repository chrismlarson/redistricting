from os import path
from exportData.displayShapes import plotBlocksFromRedistrictingGroup
from exportData.exportData import saveDataToFile, exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsFromCensusData


blockFilePath = path.expanduser('~/Documents/2010-Michigan-KeweenawAndInghamBlockInfo.redistdata')
redistrictingGroupList = createRedistrictingGroupsFromCensusData(filePath=blockFilePath)
exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='KeweenawAndInghamRedistrictingGroups')

for redistrictingGroup in redistrictingGroupList:
    plotBlocksFromRedistrictingGroup(redistrictingGroup=redistrictingGroup)
temp = 0
