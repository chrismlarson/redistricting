import sys
from us import states
from exportData.displayShapes import plotBlocksForRedistrictingGroups
from exportData.exportData import saveDataToFileWithDescription,\
    loadDataFromFileWithDescription  # , exportGeographiesToShapefile
from formatData.redistrictingGroup import createRedistrictingGroupsWithAtomicBlocksFromCensusData, \
    prepareGraphsForRedistrictingGroups, prepareBlockGraphsForRedistrictingGroups, mergeContiguousRedistrictingGroups

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = int(sys.argv[1]) if len(sys.argv) > 1 else 2010
descriptionToWorkWith = 'All'

censusData = loadDataFromFileWithDescription(censusYear=censusYear,
                                             stateName=stateInfo.name,
                                             descriptionOfInfo='{0}Block'.format(descriptionToWorkWith))
redistrictingGroupList = createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData=censusData)
# exportGeographiesToShapefile(geographyList=AtomicBlock.atomicBlockList, descriptionOfInfo='AtomicGroups')
saveDataToFileWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroupPreGraph'.format(descriptionToWorkWith))

redistrictingGroupList = prepareBlockGraphsForRedistrictingGroups(redistrictingGroupList)
saveDataToFileWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroupBlockGraphsPrepared'
                              .format(descriptionToWorkWith))

redistrictingGroupList = prepareGraphsForRedistrictingGroups(redistrictingGroupList)
saveDataToFileWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}RedistrictingGroup'.format(descriptionToWorkWith))

redistrictingGroupList = mergeContiguousRedistrictingGroups(redistrictingGroupList)
saveDataToFileWithDescription(data=redistrictingGroupList,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}MergedRedistrictingGroup'.format(descriptionToWorkWith))

plotBlocksForRedistrictingGroups(redistrictingGroups=redistrictingGroupList,
                                 showDistrictNeighborConnections=True)
