from us import states
from exportData.exportData import saveDataToFile, loadDataFromFileWithDescription
from redistrict.district import createDistrictFromRedistrictingGroups, splitDistrict

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'Charlevoix'


redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))

initialDistrict = createDistrictFromRedistrictingGroups(redistrictingGroups=redistrictingGroups)
districts = splitDistrict(districtToSplit=initialDistrict, numberOfDistricts=1)
temp=0