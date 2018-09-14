import geographyHelper
import censusCounty
from tqdm import tqdm
from censusGeography import CensusGeography


class CensusBlock(CensusGeography):
    def __init__(self, countyFIPS, tractFIPS, blockFIPS, population, geoJSONGeometry):
        CensusGeography.__init__(self, FIPS=blockFIPS, geoJSONGeometry=geoJSONGeometry)
        self.id = uniqueBlockIdentifierFromFIPS(countyFIPS, tractFIPS, self.FIPS)
        self.countyFIPS = countyFIPS
        self.tractFIPS = tractFIPS
        self.population = population
        CensusBlock.blockList.append(self)
        self.parentCounty = censusCounty.getCountyWithFIPS(countyFIPS=countyFIPS)

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
            censusBlocks.append(CensusBlock(countyFIPS=rawBlock['county'],
                                            tractFIPS=rawBlock['tract'],
                                            blockFIPS=rawBlock['block'],
                                            population=rawBlock['population'],
                                            geoJSONGeometry=rawBlock['geometry']))
            pbar.update(1)
    return censusBlocks
