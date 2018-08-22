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

def getBlockGeoData(blockInfo):
    #todo: figure out how to get this info online
    #the documentation: https://tigerweb.geo.census.gov/arcgis/sdk/rest/index.html#/Getting_started/02ss00000048000000/
    #the likely endpoint: https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14?f=json
    temp = 0

def saveBlockInfoToCSV(blockInfo, censusYear, stateName):
    csvPath = path.expanduser('~/Documents/{0}-{1}-BlockInfo.csv'.format(censusYear, stateName))
    keys = blockInfo[0].keys()
    with open(csvPath, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(blockInfo)

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010

censusRequest = Census(apiKeys.censusAPIKey, year=censusYear)

countyInfoList = getCountiesInState(stateFIPSCode=stateInfo.fips)
allBlocksInState = getAllBlocksInState(countyList=countyInfoList, maxNumberOfCounties=math.inf)
#todo: get shapefiles or neighboring blocks for each block

#save list to csv
saveBlockInfoToCSV(blockInfo=allBlocksInState, censusYear=censusYear, stateName=stateInfo.name)