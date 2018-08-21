from census import Census
from us import states
import math
import csv
from os import path
import apiKeys


def getCountiesInState(stateFIPSCode):
    allCountiesInState = censusRequest.sf1.get(fields=('NAME'), geo={'for': 'county:*',
                                                                     'in': 'state:{0}'.format(
                                                                         stateFIPSCode)})
    return allCountiesInState

def getBlocksInCounty(stateFIPSCode, countyFIPSCode):
    # P0010001 is the total population as defined by: https://api.census.gov/data/2010/sf1/variables.html
    countyBlocks = censusRequest.sf1.get(fields=('NAME', 'P0010001'), geo={'for': 'block:*',
                                                                           'in': 'state:{0} county:{1}'.format(
                                                                               stateFIPSCode, countyFIPSCode)})
    return countyBlocks

def getAllBlocksInState(countyList, maxNumberOfCounties=math.inf):
    fullBlockList = []

    # getting population counts and Block names for each county
    count = 0
    for county in countyList:
        if count >= maxNumberOfCounties:
            break
        countyFIPS = county['county']
        blocksInCounty = getBlocksInCounty(stateFIPSCode=county['state'], countyFIPSCode=countyFIPS)
        fullBlockList += blocksInCounty
        print('Got info on {0}'.format(county['NAME']))
        count += 1

    return fullBlockList

def saveBlockInfoToCSV(blockInfo, censusYear, stateName):
    csvPath = path.expanduser('~/{0}-{1}-BlockInfo.csv'.format(censusYear, stateName))
    #todo: save to csv. maybe try this code: https://gis.stackexchange.com/questions/72458/export-list-of-values-into-csv-or-txt-file

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010

censusRequest = Census(apiKeys.censusAPIKey, year=censusYear)

countyInfoList = getCountiesInState(stateFIPSCode=stateInfo.fips)
allBlocksInState = getAllBlocksInState(countyList=countyInfoList, maxNumberOfCounties=5)
#todo: get shapefiles or neighboring blocks for each block

#save list to csv
saveBlockInfoToCSV(blockInfo=allBlocksInState, censusYear=censusYear, stateName=stateInfo.name)