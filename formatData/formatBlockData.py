from os import path
from exportData.exportData import saveDataToFile, exportGeographiesToShapefile
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import createRedistrictingGroupsFromCensusData

#
# def getRawDictData(csvPath):
#     csvHelper.setCSVLimitToMaxAcceptable()
#     numOfCSVRows = csvHelper.getNumOfCSVRows(csvPath=csvPath)
#
#     tqdm.write('*** Loading CSV data ***')
#     rawDictData = []
#     with tqdm(total=numOfCSVRows) as pbar:
#         with open(csvPath, newline='\n') as csvFile:
#             dictReader = csv.DictReader(csvFile)
#             for row in dictReader:
#                 if 'P0010001' in row:
#                     population = row.pop('P0010001', None)
#                     row['population'] = population
#                 rowGeometry = ast.literal_eval(row['geometry'])
#                 row['geometry'] = rowGeometry
#                 rawDictData.append(row)
#                 pbar.update(1)
#
#     return rawDictData
#

# countyCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamCountyInfo.csv')
# rawCountyData = getRawDictData(csvPath=countyCSVPath)
#
# blockCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamBlockInfo.csv')
# rawBlockData = getRawDictData(csvPath=blockCSVPath)
#
# countyList = censusCounty.createCountiesFromRawData(rawCountyData=rawCountyData)
# #exportData.exportGeographiesToShapefile(geographyList=countyList, descriptionOfInfo='Counties')
#
# blockList = censusBlock.createCensusBlocksFromRawData(rawBlockData=rawBlockData)
#
# initialRedistrictingGroups = redistrictingGroup.createRedistrictingGroupsFromCounties()
# exportData.exportGeographiesToShapefile(geographyList=initialRedistrictingGroups, descriptionOfInfo='InitialRedistrictingGroups')

blockFilePath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamBlockInfo.redistdata')
redistrictingGroupList = createRedistrictingGroupsFromCensusData(filePath=blockFilePath)
exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFile(data=redistrictingGroupList, censusYear='2010', stateName='Michigan',
               descriptionOfInfo='ThumbPlusInghamRedistrictingGroups')

temp = 0
