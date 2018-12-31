from censusData.censusGeography import CensusGeography


class ExistingDistrict(CensusGeography):
    def __init__(self, districtNumber, geoJSONGeometry=None, geometry=None):
        CensusGeography.__init__(self, FIPS=districtNumber, geoJSONGeometry=geoJSONGeometry, geometry=geometry)
