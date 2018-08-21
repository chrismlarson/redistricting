from census import Census
from us import states
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


censusRequest = Census(apiKeys.censusAPIKey, year=2010)

stateFIPS = states.MI.fips

countyInfoList = getCountiesInState(stateFIPSCode=stateFIPS)
fullBlockList = []

for county in countyInfoList:
    countyFIPS = county['county']
    blocksInCounty = getBlocksInCounty(stateFIPSCode=stateFIPS, countyFIPSCode=countyFIPS)
    fullBlockList += blocksInCounty
    print('Got info on {0}'.format(county['NAME']))
