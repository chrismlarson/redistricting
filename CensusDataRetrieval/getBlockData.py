from census import Census
from us import states
import apiKeys
import math


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


censusRequest = Census(apiKeys.censusAPIKey, year=2010)

stateFIPS = states.MI.fips

countyInfoList = getCountiesInState(stateFIPSCode=stateFIPS)
allBlocksInState = getAllBlocksInState(countyList=countyInfoList)

#todo: get shapefiles or neighboring blocks for each block
