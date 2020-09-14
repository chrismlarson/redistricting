from us import states
from exportData.displayShapes import plotDistricts, plotPolygons
from exportData.exportData import loadDataFromFileWithDescription, saveDataToFileWithDescription, \
    saveGeoJSONToDirectoryWithDescription
from geographyHelper import populationDeviationFromPercent
from redistrict.district import createDistrictFromRedistrictingGroups, WeightingMethod, BreakingMethod

stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'
numberOfDistricts = 110
overallPercentageOffIdealAllowed = 0.0996

redistrictingGroups = loadDataFromFileWithDescription(censusYear=censusYear,
                                                      stateName=stateInfo.name,
                                                      descriptionOfInfo='{0}RedistrictingGroup'.format(
                                                          descriptionToWorkWith))

initialDistrict = createDistrictFromRedistrictingGroups(redistrictingGroups=redistrictingGroups)

populationDeviation = populationDeviationFromPercent(overallPercentage=overallPercentageOffIdealAllowed,
                                                     numberOfDistricts=numberOfDistricts,
                                                     totalPopulation=initialDistrict.population)

districts = initialDistrict.splitDistrict(numberOfDistricts=numberOfDistricts,
                                          populationDeviation=populationDeviation,
                                          weightingMethod=WeightingMethod.cardinalDistance,
                                          breakingMethod=BreakingMethod.splitBestCandidateGroup,
                                          shouldMergeIntoFormerRedistrictingGroups=True,
                                          shouldDrawEachStep=False,
                                          shouldRefillEachPass=True,
                                          fastCalculations=False,
                                          showDetailedProgress=False)
saveDataToFileWithDescription(data=districts,
                              censusYear=censusYear,
                              stateName=stateInfo,
                              descriptionOfInfo='{0}-FederalDistricts'.format(descriptionToWorkWith))
saveGeoJSONToDirectoryWithDescription(geographyList=districts,
                                      censusYear=censusYear,
                                      stateName=stateInfo,
                                      descriptionOfInfo='FederalDistrictsGeoJSON')
plotDistricts(districts=districts,
              showPopulationCounts=False,
              showDistrictNeighborConnections=False)
districtPolygons = [district.geometry for district in districts]
plotPolygons(districtPolygons)
