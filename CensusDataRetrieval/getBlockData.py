from census import Census
from us import states
import math
import csv
from os import path
from esridump.dumper import EsriDumper
import apiKeys


def getCountiesInState(stateFIPSCode):
    allCountiesInState = censusRequest.sf1.get(fields=('NAME'), geo={'for': 'county:*',
                                                                     'in': 'state:{0}'.format(
                                                                         stateFIPSCode)})
    return allCountiesInState


def getBlocksInCounty(stateFIPSCode, countyFIPSCode):
    # P0010001 is the total population as defined by: https://api.census.gov/data/2010/sf1/variables.html
    countyBlocks = censusRequest.sf1.get(fields=('P0010001'),
                                         geo={'for': 'block:*', 'in': 'state:{0} county:{1}'.format(
                                             stateFIPSCode, countyFIPSCode)})
    return countyBlocks


def getAllBlocksInState(countyList, maxNumberOfCounties=math.inf):
    fullBlockList = []

    # getting population counts and Block names for each county
    print('*** Getting all blocks and population counts in state ***')
    count = 0
    for county in countyList:
        if count >= maxNumberOfCounties:
            break
        countyFIPS = county['county']
        blocksInCounty = getBlocksInCounty(stateFIPSCode=county['state'], countyFIPSCode=countyFIPS)
        fullBlockList += blocksInCounty
        print('Got all blocks and population counts in {0}'.format(county['NAME']))
        count += 1

    return fullBlockList


def allGeoDataForEachBlock(existingBlockData, countyInfoListForProgress):
    if (len(existingBlockData) > 0):
        print('*** Getting geo info on all blocks ***')
        stateFIPSCode = existingBlockData[0]['state']
        blockGeometries = EsriDumper(
            url='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14',
            extra_query_args={'where': 'STATE=\'{0}\''.format(stateFIPSCode),
                              'orderByFields':'COUNTY'})
        # https://github.com/openaddresses/pyesridump

        fullBlockListWithGeo = []
        currentCounty = None
        for blockGeometry in blockGeometries:
            blockGeoProperties = blockGeometry['properties']
            blockGeoStateFIPS = blockGeoProperties['STATE']
            blockGeoCountyFIPS = blockGeoProperties['COUNTY']
            blockGeoTractFIPS = blockGeoProperties['TRACT']
            blockGeoBlockFIPS = blockGeoProperties['BLOCK']

            if(currentCounty != blockGeoCountyFIPS):
                currentCounty = blockGeoCountyFIPS
                county = next((item for item in countyInfoListForProgress if item['county'] == currentCounty), None)
                print('Getting all geo info in {0}'.format(county['NAME']))

            mathchingBlockData = next((item for item in existingBlockData if
                                       item['state'] == blockGeoStateFIPS and
                                       item['county'] == blockGeoCountyFIPS and
                                       item['tract'] == blockGeoTractFIPS and
                                       item['block'] == blockGeoBlockFIPS), None)
            mathchingBlockData['geometry'] = blockGeometry['geometry']
            fullBlockListWithGeo.append(mathchingBlockData)
        return fullBlockListWithGeo
    else:
        return None


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
allBlockGeosInState = allGeoDataForEachBlock(existingBlockData=allBlocksInState, countyInfoListForProgress=countyInfoList)

# save list to csv
saveBlockInfoToCSV(blockInfo=allBlockGeosInState, censusYear=censusYear, stateName=stateInfo.name)
