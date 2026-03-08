from us import states
from exportData.displayShapes import plotDistrictComparison
from exportData.exportData import loadDataFromFileWithDescription

stateInfo = states.lookup('MI')
descriptionToWorkWith = 'All'

districts2010 = loadDataFromFileWithDescription(censusYear=2010, stateName=stateInfo.name,
                                                descriptionOfInfo=f'{descriptionToWorkWith}-FederalDistricts')
districts2020 = loadDataFromFileWithDescription(censusYear=2020, stateName=stateInfo.name,
                                                descriptionOfInfo=f'{descriptionToWorkWith}-FederalDistricts')
plotDistrictComparison(districts2010, districts2020)
