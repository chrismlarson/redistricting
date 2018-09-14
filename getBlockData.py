from census import Census
from us import states
import math
import csv
from os import path
from esridump.dumper import EsriDumper
import time
import apiKeys


def getCountiesInState(stateFIPSCode, maxNumberOfCounties=math.inf, specificCountiesOnly=None):
    requestedCounties = censusRequest.sf1.get(fields=('NAME'),
                                              geo={'for': 'county:*', 'in': 'state:{0}'.format(stateFIPSCode)})
    if specificCountiesOnly != None:
        listOfSpecificCounties = []
        for specificCounty in specificCountiesOnly:
            matchingCounty = next((item for item in requestedCounties if
                                   item['NAME'] == '{0} County'.format(specificCounty)), None)
            listOfSpecificCounties.append(matchingCounty)
        requestedCounties = listOfSpecificCounties

    if maxNumberOfCounties == math.inf:
        maxNumberOfCounties = len(requestedCounties)
        requestedCounties = requestedCounties[:maxNumberOfCounties]

    return requestedCounties


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
                                  'orderByFields': 'TRACT, BLKGRP, BLOCK'},
                timeout=120)  # extending timeout because there were some long load times
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
            elapsedSecondsForProcessingCounty = (
                    time.mktime(endTimeForProcessingCounty) - time.mktime(startTimeForProcessingCounty))
            print('   {0} took {1} seconds'.format(county['NAME'], elapsedSecondsForProcessingCounty))

        endTimeForProcessingState = time.localtime()
        elapsedMinutesForProcessingState = (time.mktime(endTimeForProcessingState) - time.mktime(
            startTimeForProcessingState)) / 60
        print('It took {0} total minutes to get all the requested block geo data'.format(
            elapsedMinutesForProcessingState))
        return fullBlockListWithGeo
    else:
        return None


def allGeoDataForEachCounty(existingCountyData):
    if len(existingCountyData) > 0:
        print('*** Getting geo info on all counties ***')
        stateFIPSCode = existingCountyData[0]['state']

        startTimeForProcessingState = time.localtime()
        fullCountyListWithGeo = []

        whereArgument = 'STATE=\'{0}\' AND ('.format(stateFIPSCode)
        for county in existingCountyData:
            whereArgument = '{0}NAME=\'{1}\''.format(whereArgument, county['NAME'])
            if existingCountyData.index(county) != len(existingCountyData) - 1:
                whereArgument = '{0} OR '.format(whereArgument)
        whereArgument = '{0})'.format(whereArgument)

        countyGeometries = EsriDumper(
            url='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/90',
            extra_query_args={'where': whereArgument,
                              'orderByFields': 'COUNTY'})
        # https://github.com/openaddresses/pyesridump

        for countyGeometry in countyGeometries:
            countyGeoProperties = countyGeometry['properties']
            countyGeoStateFIPS = countyGeoProperties['STATE']
            countyGeoCountyFIPS = countyGeoProperties['COUNTY']

            matchingCountyData = next((item for item in existingCountyData if
                                       item['state'] == countyGeoStateFIPS and
                                       item['county'] == countyGeoCountyFIPS), None)
            matchingCountyData['geometry'] = countyGeometry['geometry']
            fullCountyListWithGeo.append(matchingCountyData)

        endTimeForProcessingState = time.localtime()
        elapsedMinutesForProcessingState = (
                time.mktime(endTimeForProcessingState) - time.mktime(startTimeForProcessingState))
        print('It took {0} total seconds to get all the requested county geo data'.format(
            elapsedMinutesForProcessingState))
        return fullCountyListWithGeo
    else:
        return None


def saveInfoToCSV(info, censusYear, stateName, descriptionOfInfo):
    csvPath = path.expanduser('~/Documents/{0}-{1}-{2}Info.csv'.format(censusYear, stateName, descriptionOfInfo))
    keys = info[0].keys()
    with open(csvPath, 'w') as output_file:
        dictWriter = csv.DictWriter(output_file, keys)
        dictWriter.writeheader()
        dictWriter.writerows(info)

    return csvPath


stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010

censusRequest = Census(apiKeys.censusAPIKey, year=censusYear)

countyInfoList = getCountiesInState(stateFIPSCode=stateInfo.fips, maxNumberOfCounties=math.inf,
                                    specificCountiesOnly={'Huron', 'Tuscola', 'Sanilac', 'Ingham'})
allCountyGeosInState = allGeoDataForEachCounty(existingCountyData=countyInfoList)
# save county data to csv
saveInfoToCSV(info=allCountyGeosInState, censusYear=censusYear, stateName=stateInfo.name,
              descriptionOfInfo='ThumbPlusInghamCounty')

allBlocksInState = getAllBlocksInState(countyList=countyInfoList)
allBlockGeosInState = allGeoDataForEachBlock(countyInfoList=countyInfoList, existingBlockData=allBlocksInState)
# save block data to csv
saveInfoToCSV(info=allBlockGeosInState, censusYear=censusYear, stateName=stateInfo.name, descriptionOfInfo='ThumbPlusInghamBlock')
