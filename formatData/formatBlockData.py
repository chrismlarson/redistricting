import csv
from os import path
import ast
from tqdm import tqdm
from censusData import censusCounty, censusBlock
import csvHelper
from formatData import redistrictingGroup
from exportData import exportData


def getRawDictData(csvPath):
    csvHelper.setCSVLimitToMaxAcceptable()
    numOfCSVRows = csvHelper.getNumOfCSVRows(csvPath=csvPath)

    tqdm.write('*** Loading CSV data ***')
    rawDictData = []
    with tqdm(total=numOfCSVRows) as pbar:
        with open(csvPath, newline='\n') as csvFile:
            dictReader = csv.DictReader(csvFile)
            for row in dictReader:
                if 'P0010001' in row:
                    population = row.pop('P0010001', None)
                    row['population'] = population
                rowGeometry = ast.literal_eval(row['geometry'])
                row['geometry'] = rowGeometry
                rawDictData.append(row)
                pbar.update(1)

    return rawDictData


countyCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamCountyInfo.csv')
rawCountyData = getRawDictData(csvPath=countyCSVPath)

blockCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbPlusInghamBlockInfo.csv')
rawBlockData = getRawDictData(csvPath=blockCSVPath)

countyList = censusCounty.createCountiesFromRawData(rawCountyData=rawCountyData)
#exportData.exportGeographiesToShapefile(geographyList=countyList, descriptionOfInfo='Counties')

blockList = censusBlock.createCensusBlocksFromRawData(rawBlockData=rawBlockData)

initialRedistrictingGroups = redistrictingGroup.createRedistrictingGroupsFromCounties()
exportData.exportGeographiesToShapefile(geographyList=initialRedistrictingGroups, descriptionOfInfo='InitialRedistrictingGroups')

temp = 0