import geographyHelper


class CensusBlocks:
    def __init__(self, countyFIPS, tractFIPS, blockFIPS, population, geoJSONGeometry):
        self.id = uniqueBlockIdentifierFromFIPS(countyFIPS, tractFIPS, blockFIPS)
        self.countyFIPS = countyFIPS
        self.tractFIPS = tractFIPS
        self.blockFIPS = blockFIPS
        self.population = population
        self.geometry = geographyHelper.convertGeoJSONToShapely(geoJSONGeometry)
        self.borderingCounties = []
        CensusBlocks.blockList.append(self)

    blockList = []


def uniqueBlockIdentifierFromFIPS(countyFIPS, tractFIPS, blockFIPS):
    return '{0}-{1}-{2}'.format(countyFIPS, tractFIPS, blockFIPS)


def createCensusBlocksFromRawData(rawBlockData):
    censusBlocks = []
    for rawBlock in rawBlockData:
        censusBlocks.append(CensusBlocks(countyFIPS=rawBlock['county'],
                                         tractFIPS=rawBlock['tract'],
                                         blockFIPS=rawBlock['block'],
                                         population=rawBlock['population'],
                                         geoJSONGeometry=rawBlock['geometry']))
    return censusBlocks
