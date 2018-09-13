import json
from esridump.dumper import EsriDumper
import shapely.geometry

#blockGeometries = EsriDumper('https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14', extra_query_args={'where': 'STATE=\'26\' AND COUNTY=\'065\''}) #get all blocks in Ingham County, MI (fips:065)
#blockGeometries = EsriDumper('https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14', extra_query_args={'where': 'STATE=\'26\'','orderByFields':'COUNTY'}) #get all blocks in Michigan (fips:26)

#https://github.com/openaddresses/pyesridump

# Iterate over each feature
#for blockGeometry in blockGeometries:
#    print(json.dumps(blockGeometry))



a = shapely.geometry.Polygon([[0, 0], [0, 10], [10, 10], [10, 0]])
b = shapely.geometry.Polygon([[0, 2], [0, 3], [1, 3], [1, 2]])
c = shapely.geometry.Polygon([[5, 3], [5, 4], [6, 4], [6, 3]])
d = shapely.geometry.Polygon([[-1, 2], [-1, 3], [1, 3], [1, 2]])

# print(a.contains(b))
# print(a.within(b))
# print(a.crosses(b))
# print(a.disjoint(b))
# print(a.intersects(b))
# print(a.overlaps(b))
# print(a.touches(b))
# print(a.almost_equals(b))
#
# print()
#
# print(b.contains(a))
# print(b.within(a))
# print(b.crosses(a))
# print(b.disjoint(a))
# print(b.intersects(a))
# print(b.overlaps(a))
# print(b.touches(a))
# print(b.almost_equals(a))
#
# print()

print(a.boundary.contains(b.boundary))
print(a.boundary.within(b.boundary))
print(a.boundary.crosses(b.boundary))
print(a.boundary.disjoint(b.boundary))
print(a.boundary.intersects(b.boundary))
print(a.boundary.overlaps(b.boundary))
print(a.boundary.touches(b.boundary))
print(a.boundary.almost_equals(b.boundary))

print()

print(a.boundary.contains(c.boundary))
print(a.boundary.within(c.boundary))
print(a.boundary.crosses(c.boundary))
print(a.boundary.disjoint(c.boundary))
print(a.boundary.intersects(c.boundary))
print(a.boundary.overlaps(c.boundary))
print(a.boundary.touches(c.boundary))
print(a.boundary.almost_equals(c.boundary))

print()

print(a.boundary.contains(d.boundary))
print(a.boundary.within(d.boundary))
print(a.boundary.crosses(d.boundary))
print(a.boundary.disjoint(d.boundary))
print(a.boundary.intersects(d.boundary))
print(a.boundary.overlaps(d.boundary))
print(a.boundary.touches(d.boundary))
print(a.boundary.almost_equals(d.boundary))


temp = 0