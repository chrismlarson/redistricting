from us import states
from exportData.displayShapes import plotDistrict, plotDistricts
from exportData.exportData import saveDataToFile, loadDataFromFileWithDescription
from redistrict.district import createDistrictFromRedistrictingGroups, splitDistrict

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))

initialDistrict = createDistrictFromRedistrictingGroups(redistrictingGroups=redistrictingGroups)
# plotDistrict(district=initialDistrict, showDistrictNeighborConnections=True, showDistrictEnvelope=True, colorDirectionalGroups=True)
districts = splitDistrict(districtToSplit=initialDistrict, numberOfDistricts=14, populationDeviation=1, shouldDrawEachStep=True)
plotDistricts(districts=districts,
              showPopulationCounts=True,
              showDistrictNeighborConnections=True)
temp = 0
