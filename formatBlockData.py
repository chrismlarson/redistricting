import csv
from os import path
import ast
import sys
from tqdm import tqdm
import counties
import exportData

def getNumOfCSVRows(csvPath):
    setCSVLimitToMaxAcceptable()

    print('*** Getting total number of CSV rows for progress ***')
    totalNumberOfRows = 0
    with tqdm() as pbar:
        with open(csvPath, newline='\n') as csvFile:
            dictReader = csv.DictReader(csvFile)
            for row in dictReader:
                totalNumberOfRows += 1
                pbar.update(1)
            pbar.clear()

    totalNumberOfRows -= 1 #to account for the header
    print('Total number of CSV rows: {0}'.format(totalNumberOfRows))
    return totalNumberOfRows


def setCSVLimitToMaxAcceptable():
    decrement = True
    maxInt = sys.maxsize

    while decrement:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        decrement = False
        try:
            csv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt / 10)
            decrement = True


def getRawDictData(csvPath):
    setCSVLimitToMaxAcceptable()
    numOfCSVRows = getNumOfCSVRows(csvPath=csvPath)

    print('*** Loading raw CSV data ***')
    rawDictData = []
    with tqdm(total=numOfCSVRows) as pbar:
        with open(csvPath, newline='\n') as csvFile:
            dictReader = csv.DictReader(csvFile)
            for row in dictReader:
                rowGeometry = ast.literal_eval(row['geometry'])
                row['geometry'] = rowGeometry
                rawDictData.append(row)
                pbar.update(1)

    return rawDictData

countyCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbCountyInfo.csv')
rawCountyData = getRawDictData(csvPath=countyCSVPath)

blockCSVPath = path.expanduser('~/Documents/2010-Michigan-ThumbBlockInfo.csv')
rawBlockData = getRawDictData(csvPath=blockCSVPath)

counties = counties.createCountiesFromRawData(rawCountyData=rawCountyData)
exportData.exportCountiesToShapefile(counties)

temp = 0