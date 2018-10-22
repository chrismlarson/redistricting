from exportData.displayShapes import plotBlocksFromRedistrictingGroup
from exportData.exportData import loadDataFromFile
from formatData.atomicBlock import createAtomicBlocksFromBlockList
from formatData.blockGraph import BlockGraph
from censusData import censusBlock
import geographyHelper
from tqdm import tqdm


class RedistrictingGroup(BlockGraph):
    def __init__(self, childrenBlocks):
        BlockGraph.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []


def updateAllBlockContainersData():
    tqdm.write('*** Updating All Block Container Data ***')
    with tqdm(total=len(RedistrictingGroup.redistrictingGroupList)) as pbar:
        for blockContainer in RedistrictingGroup.redistrictingGroupList:
            tqdm.write('   *** One more ***')
            blockContainer.updateBlockContainerData()
            pbar.update(1)


def setBorderingRedistrictingGroups(redistrictingGroupList):
    for redistrictingGroupToCheck in redistrictingGroupList:
        for redistrictingGroupToCheckAgainst in redistrictingGroupList:
            if redistrictingGroupToCheck != redistrictingGroupToCheckAgainst:
                if geographyHelper.intersectingGeometries(redistrictingGroupToCheck, redistrictingGroupToCheckAgainst):
                    redistrictingGroupToCheck.neighboringGroups.append(redistrictingGroupToCheckAgainst)


def getRedistrictingGroupWithCountyFIPS(countyFIPS):
    # for use when first loading redistricting group
    return next((item for item in RedistrictingGroup.redistrictingGroupList if item.FIPS == countyFIPS), None)


def convertAllCensusBlocksToAtomicBlocks():
    tqdm.write('\n')
    tqdm.write('*** Converting All Census Blocks to Atomic Blocks ***')
    count = 1
    for blockContainer in RedistrictingGroup.redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Converting to Atomic Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(RedistrictingGroup.redistrictingGroupList)))
        atomicBlocksForGroup = createAtomicBlocksFromBlockList(blockList=blockContainer.blocks)
        blockContainer.blocks = atomicBlocksForGroup  # this triggers a block container update


def createRedistrictingGroupsFromCensusData(filePath):
    censusData = loadDataFromFile(filePath=filePath)
    tqdm.write('\n')
    tqdm.write('*** Creating Redistricting Groups from Census Data ***')
    redistrictingGroupList = []
    with tqdm(total=len(censusData)) as pbar:
        for censusBlockDict in censusData:
            redistrictingGroupWithCountyFIPS = getRedistrictingGroupWithCountyFIPS(censusBlockDict['county'])
            if redistrictingGroupWithCountyFIPS is None:
                redistrictingGroupWithCountyFIPS = RedistrictingGroup(childrenBlocks=[])
                redistrictingGroupWithCountyFIPS.FIPS = censusBlockDict['county']
                redistrictingGroupList.append(redistrictingGroupWithCountyFIPS)

            isWater = False
            if censusBlockDict['block'][0] == '0':
                isWater = True
            blockFromCSV = censusBlock.CensusBlock(countyFIPS=censusBlockDict['county'],
                                                   tractFIPS=censusBlockDict['tract'],
                                                   blockFIPS=censusBlockDict['block'],
                                                   population=int(censusBlockDict['P0010001']),
                                                   isWater=isWater,
                                                   geoJSONGeometry=censusBlockDict['geometry'])
            redistrictingGroupWithCountyFIPS.blocks.append(blockFromCSV)
            pbar.update(1)

    # convert census blocks to atomic blocks
    convertAllCensusBlocksToAtomicBlocks()

    # find and set neighboring geometries
    setBorderingRedistrictingGroups(redistrictingGroupList=redistrictingGroupList)

    # remove FIPS info from the groups to not pollute data later
    for redistrictingGroup in redistrictingGroupList:
        del redistrictingGroup.FIPS

    return redistrictingGroupList
