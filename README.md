# Redistricting
Fair US state redistricting experiments without using demographic info beyond location.

## The problems

#### Not every vote is equal
Using Michigan as an example. In the 2012 election (after the last round of redistricting), these were the congressional election results statewide:

|                    | Republican | Democratic |
|--------------------|------------|------------|
| Seats won          | 9          | 5          |
| Total vote         | 2,086,804  | 2,327,985  |
| Percentage of vote | 45.62%     | 50.89%     |

[Data taken from Wikipedia](https://en.wikipedia.org/wiki/United_States_House_of_Representatives_elections_in_Michigan,_2012)

It certainly doesn't look correct that Democratic candidates could have been voted for in stronger numbers, but won 4 fewer seats. These voters aren't been accurately represented in Congress. 

#### Redistricting is biased when done by humans
Gerrymandering is a practice that has historically been used to defend incumbents. But more recently, it has been used more effectively to lock in US congressional control.

More advanced practices of using gender, race, age, buying habits, and party affiliation.

Even using the Voting Rights Act has been used as an excuse for creating districts.

#### Both the Democratic and Republican parties have gerrymandered 
While the current Republican control of most states is currently responsible for most of the gerrymandering around the country, it has been used by both parties in the past.

#### Extreme and uncompromising representatives
By having uncompetitive districts, it forces any real competition down to the primaries for each party. And when a politician only needs to compete in the primaries of their party, any history of working with the other party is potentially a liability, so representatives steer away from it. Leading to further polarization of representation.

## The solutions others have suggested

#### Independent commissions
While effective is some states, it relies too much on individuals to behave rationally and without bias or corruption. While people on commissions may have the best interest of the voters at heart, there will ultimately be some bias in their decisions.

Further, if they are given maps from outside the commission, they could approve maps that appear to be fair currently but won't be in a few years. There have been advances in data collection and analysis that make it possible to create gerrymandered maps based on predicting population aging and migrations.

#### Make all districts competitive
When most people discuss competitive voting districts, they are referring to districts that have close to the same number of Democrats and Republicans. There are some problems with this.
* It further ingrains just those two parties into our political system
* At what cost do we create competitive districts? If people choose to live with like-minded individuals, that's their choice.
   * This is an attempt to remove unnatural non-competitiveness. Not combat the so-called [Big Sort](http://www.thebigsort.com/home.php).

## Proposed Solution
Evenly split a state into a set number of districts by using county lines and population borders while keeping districts as compact as possible.

### Rules we will follow

#### Keep communities together
By using the [2010 US Census data](https://www2.census.gov/census_2010/04-Summary_File_1/Michigan/), this experiment will break up each state (starting with Michigan) into individual census blocks (the smallest population Census unit). With those blocks, form a population density map. From that map, attempt to keep population groups together by creating paths through the population map that don't break up population dense areas.

The first attempts will start using [Dijkstra's_algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm). It's a method similar to those used in finding seams in [Seam Carving](https://en.wikipedia.org/wiki/Seam_carving#Computing_seams) (a image resizing method).

Hopefully by doing this maps will naturally comply with the Voting Rights Act, but as mentioned before, using demographics other than location can lead to bias. So this experiment won't be using any of that information. And will leave the evaluation of the maps under the Voting Rights Act to third parties after the fact. 

#### Use population borders
Using only (in this order):
* County lines
* Community lines (mentioned above)
* Census blocks

Possibly others as the experiments progress (while adhering to the other rules).

#### Keep districts as round as possible
Using the [Polsby-Popper Test](https://en.wikipedia.org/wiki/Polsby-Popper_Test) and setting a threshold. If a district doesn't meet that threshold, that electoral map won't be acceptable.

### Potential problems
The experiment results may break up rural areas more than urban areas, so we may need to find path that follow the edges of population dense areas. But in the theme of keeping this simple, we will first rely on the roundness/compactness tests first to overcome this challenge.

## Notes
Notice that we are only using population maps to create the district maps
