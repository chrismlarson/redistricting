from us import states
from esridump.dumper import EsriDumper
from censusData.existingDistrict import ExistingDistrict
from exportData.exportData import saveDataToFileWithDescription, saveGeoJSONToDirectoryWithDescription


def getAllGeoDataForFederalCongressionalDistricts(stateFIPSCode):
    districtGeometries = EsriDumper(
        url='https://tigerweb.geo.census.gov/arcgis/rest/services/Generalized_ACS2017/Legislative/MapServer/5',
        extra_query_args={'where': 'STATE=\'{0}\''.format(stateFIPSCode)})
    # https://github.com/openaddresses/pyesridump

    existingDistricts = []
    for districtGeometry in districtGeometries:
        geoJSONGeometry = districtGeometry['geometry']
        districtNumber = districtGeometry['properties']['BASENAME']
        existingDistrict = ExistingDistrict(districtNumber=districtNumber, geoJSONGeometry=geoJSONGeometry)
        existingDistricts.append(existingDistrict)

    return existingDistricts


stateAbbreviation = 'MI'
stateInfo = states.lookup(stateAbbreviation)
censusYear = 2010
descriptionToWorkWith = 'All'

allCongressionalDistrictGeosInState = getAllGeoDataForFederalCongressionalDistricts(stateFIPSCode=stateInfo.fips)
# save county data to file
saveDataToFileWithDescription(data=allCongressionalDistrictGeosInState,
                              censusYear=censusYear,
                              stateName=stateInfo.name,
                              descriptionOfInfo='{0}CurrentFederalCongressionalDistricts'.format(descriptionToWorkWith))
saveGeoJSONToDirectoryWithDescription(geographyList=allCongressionalDistrictGeosInState,
                                      censusYear=censusYear,
                                      stateName=stateInfo.name,
                                      descriptionOfInfo='CurrentFederalCongressionalDistricts')
