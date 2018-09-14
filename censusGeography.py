import geographyHelper

class CensusGeography:
    def __init__(self, FIPS, geoJSONGeometry):
        self.FIPS = FIPS
        self.geometry = geographyHelper.convertGeoJSONToShapely(geoJSONGeometry)
