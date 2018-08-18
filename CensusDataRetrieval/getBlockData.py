from census import Census
from us import states
import apiKeys

censusRequest = Census(apiKeys.censusAPIKey, year=2010)

# P0010001 is the total population as defined by: https://api.census.gov/data/2010/sf1/variables.html
# 093 is Livingston County in Michigan's FIPS code for the 2010 US Census. This is just an example to get running
livingstonCountyBlocks = censusRequest.sf1.get(fields=('NAME', 'P0010001'), geo={'for': 'block:*', 'in':'state:{0} county:93'.format(states.MI.fips, states)})

print(livingstonCountyBlocks)