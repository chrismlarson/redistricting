from os import path
from exportData.exportData import saveDataToFile, exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsFromCensusData


blockFilePath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamBlockInfo.redistdata')
redistrictingGroupList = createRedistrictingGroupsFromCensusData(filePath=blockFilePath)
exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='ThumbPlusInghamRedistrictingGroups')

temp = 0
