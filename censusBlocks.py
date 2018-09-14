import geographyHelper
import counties
from tqdm import tqdm


class CensusBlocks:
    def __init__(self, countyFIPS, tractFIPS, blockFIPS, population, geoJSONGeometry):
        self.id = uniqueBlockIdentifierFromFIPS(countyFIPS, tractFIPS, blockFIPS)
        self.countyFIPS = countyFIPS
        self.tractFIPS = tractFIPS
        self.blockFIPS = blockFIPS
        self.population = population
        self.geometry = geographyHelper.convertGeoJSONToShapely(geoJSONGeometry)
        CensusBlocks.blockList.append(self)
        self.parentCounty = counties.getCountyWithFIPS(countyFIPS=countyFIPS)

    @property
    def parentCounty(self):
        return self.__parentCounty

    @parentCounty.setter
    def parentCounty(self, parentCounty):
        self.__parentCounty = parentCounty
        parentCounty.blocks.append(self)
        if geographyHelper.isBoundaryGeometry(parent=parentCounty, child=self):
            parentCounty.borderBlocks.append(self)

    blockList = []


def uniqueBlockIdentifierFromFIPS(countyFIPS, tractFIPS, blockFIPS):
    return '{0}-{1}-{2}'.format(countyFIPS, tractFIPS, blockFIPS)


def createCensusBlocksFromRawData(rawBlockData):
    censusBlocks = []
    print('*** Creating Blocks from raw data ***')
    with tqdm(total=len(rawBlockData)) as pbar:
        for rawBlock in rawBlockData:
            censusBlocks.append(CensusBlocks(countyFIPS=rawBlock['county'],
                                             tractFIPS=rawBlock['tract'],
                                             blockFIPS=rawBlock['block'],
                                             population=rawBlock['population'],
                                             geoJSONGeometry=rawBlock['geometry']))
            pbar.update(1)
    return censusBlocks
