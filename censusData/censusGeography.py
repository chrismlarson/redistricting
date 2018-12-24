import geographyHelper

class CensusGeography:
    def __init__(self, FIPS, geoJSONGeometry, geometry):
        if geoJSONGeometry is None and geometry is None:
            raise RuntimeError('Need to init with a geometry')
        if geoJSONGeometry is not None and geometry is not None:
            raise RuntimeError('Need to init with a single geometry')

        self.FIPS = FIPS

        if geometry is None:
            self.geometry = geographyHelper.convertGeoJSONToShapely(geoJSONGeometry)
        else:
            self.geometry = geometry
