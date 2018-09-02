from census import Census
from us import states
import math
import csv
from os import path
from esridump.dumper import EsriDumper
import time
import apiKeys


def getCountiesInState(stateFIPSCode, maxNumberOfCounties=math.inf):
    allCountiesInState = censusRequest.sf1.get(fields=('NAME'),
                                               geo={'for': 'county:*',
                                                    'in': 'state:{0}'.format(stateFIPSCode)})
    if(maxNumberOfCounties == math.inf):
        maxNumberOfCounties = len(allCountiesInState)
    allCountiesInState = allCountiesInState[:maxNumberOfCounties]
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


def allGeoDataForEachBlock(countyInfoList, existingBlockData):
    if (len(existingBlockData) > 0):
        print('*** Getting geo info on all blocks ***')
        stateFIPSCode = existingBlockData[0]['state']

        startTimeForProcessingState = time.localtime()
        fullBlockListWithGeo = []
        for county in countyInfoList:
            print('Getting all geo info in {0}'.format(county['NAME']))
            startTimeForProcessingCounty = time.localtime()
            countyFIPSCode = county['county']

            blockGeometries = EsriDumper(
                url='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14',
                extra_query_args={'where': 'STATE=\'{0}\' AND COUNTY=\'{1}\''.format(stateFIPSCode, countyFIPSCode),
                                  'orderByFields':'TRACT, BLKGRP, BLOCK'})
            # https://github.com/openaddresses/pyesridump

            for blockGeometry in blockGeometries:
                blockGeoProperties = blockGeometry['properties']
                blockGeoStateFIPS = blockGeoProperties['STATE']
                blockGeoCountyFIPS = blockGeoProperties['COUNTY']
                blockGeoTractFIPS = blockGeoProperties['TRACT']
                blockGeoBlockFIPS = blockGeoProperties['BLOCK']

                matchingBlockData = next((item for item in existingBlockData if
                                           item['state'] == blockGeoStateFIPS and
                                           item['county'] == blockGeoCountyFIPS and
                                           item['tract'] == blockGeoTractFIPS and
                                           item['block'] == blockGeoBlockFIPS), None)
                matchingBlockData['geometry'] = blockGeometry['geometry']
                fullBlockListWithGeo.append(matchingBlockData)

            endTimeForProcessingCounty = time.localtime()
            elapsedSecondsForProcessingCounty = (time.mktime(endTimeForProcessingCounty) - time.mktime(startTimeForProcessingCounty))
            print('   {0} took {1} seconds'.format(county['NAME'], elapsedSecondsForProcessingCounty))

        endTimeForProcessingState = time.localtime()
        elapsedMinutesForProcessingState = (time.mktime(endTimeForProcessingState) - time.mktime(startTimeForProcessingState)) / 60
        print('It took {0} total minutes to get all the requested block geo data'.format(elapsedMinutesForProcessingState))
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

    return csvPath


stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010

censusRequest = Census(apiKeys.censusAPIKey, year=censusYear)

countyInfoList = getCountiesInState(stateFIPSCode=stateInfo.fips, maxNumberOfCounties=2)
allBlocksInState = getAllBlocksInState(countyList=countyInfoList)
allBlockGeosInState = allGeoDataForEachBlock(countyInfoList=countyInfoList, existingBlockData=allBlocksInState)

# save list to csv
csvPath = saveBlockInfoToCSV(blockInfo=allBlockGeosInState, censusYear=censusYear, stateName=stateInfo.name)

# reader = csv.reader(open(csvPath, newline='\n'), delimiter=',', quotechar='\"')
# for row in reader:
#     print(row)
