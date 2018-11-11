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

It certainly doesn't look correct that Democratic candidates could have been voted for in stronger numbers, but won 4 fewer seats. These voters aren't being accurately represented in Congress. 

#### Redistricting is biased when done by humans
Gerrymandering is a practice that has historically been used to defend incumbents. But more recently, it has been used more effectively than ever to lock in control at the all levels of government in the US.

Modern computing has enabled more advanced practices of using gender, race, age, buying habits, and party affiliation.

Even well meaning legislation like the Voting Rights Act has been used as an excuse for creating biased districts.

**When more variables are used for redistricting, there is greater risk of misuse of the data.**

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
   
#### Other population distribution algorithms
These are similar to this experiment's proposed solution. They all eliminate any bias that may arise when using demographic data, which makes them good solutions in their own right. But there are still some issues with each that can be addressed.

##### Shortest-splitline
[The rules of this algorithm](https://en.wikipedia.org/wiki/Gerrymandering#Shortest_splitline_algorithm) use only the population distribution and geographic shape of the state to create district maps.

But problems arise when finding districts in densely populated urban areas. It tends to break them up indiscriminately. [Examples can be found here.](https://rangevoting.org/SplitLR.html)

##### Shortest average distance to center
This algorithm uses US Census blocks to creates districts where people have the lowest average distance to the center of their district.

As far as I understand this method (correct me if I'm wrong): The primary advantage of this method is that it creates fairly round and compact districts. Which the shortest travel times for constituents. It still has the same problem of potentially breaking up larger populations. That is mitigated by an element of randomness, which leads to a human choosing from a result set for the best maps. This introduces some bias into the system.

[A great explanation of the process can be found here.](https://bdistricting.com/about.html)

## Proposed Solution
Evenly split a state into a set number of districts by using county lines and population borders while keeping districts as compact as possible. Splitting is done by finding the lowest population paths through each county.

### Rules we will follow

#### Keep communities together
By using the [2010 US Census data](https://www2.census.gov/census_2010/04-Summary_File_1/Michigan/), this experiment will break up each state (starting with Michigan) into individual census blocks (the smallest population Census unit). With those blocks, form a population density map where each Census block knows its nearest neighboring blocks. Forming a state-wide population graph.

The splits will use a form of [dynamic programming used in seam carving](https://en.wikipedia.org/wiki/Seam_carving#Dynamic_programming)(an image resizing method). By finding the lowest population path through a group of Census blocks, it will avoid breaking apart communities.

Hopefully by doing this maps will naturally comply with the Voting Rights Act, but as mentioned before, using demographics other than location can lead to bias. So this experiment won't be using any of that information. And will leave the evaluation of the maps under the Voting Rights Act to third parties after map creation. 

#### Use of population borders
The algorithm starts with state county borders, an already familiar set of dividing lines to most constituents. And then will create its own split lines that will avoid population dense areas or communities. The smallest possible population group will be Census blocks.

#### Keep districts as round or compact as possible
Using the [Polsby-Popper Test](https://en.wikipedia.org/wiki/Polsby-Popper_Test) and setting a threshold. If a district doesn't meet that threshold, that electoral map won't be acceptable.

### Technical process
There are two main parts to this algorithm:
* Creating districts from a set of groups of Census blocks
* Breaking apart groups of Census blocks if the districts don't meet compactness and population requirements.
(And the algorithm will repeat until the rules are met)

When attempting to create districts, it recursively splits the state into districts of appropriately sized ratios and stops when the desired number of districts are created. The recursive splitting based on ratios is similar to the [shortest-splitline](#Shortest-splitline) method. But instead of trying to find a dividing line, it uses a [Forest Fire algorithm](https://en.wikipedia.org/wiki/Flood_fill#Alternative_implementations) to find candidate groups that most closely match the desired population ratio.

If the population ratio cannot be met or the resulting district split doesn’t meet a roundness threshold, a selection of groups are split via the method of [dynamic programming used in seam carving](https://en.wikipedia.org/wiki/Seam_carving#Dynamic_programming) that has been mentioned above.

### Potential problems
The experiment results may break up rural areas more than urban areas, so we may need to find path that follow the edges of population dense areas. But in the theme of keeping this simple, we will first rely on the roundness/compactness tests first to overcome this challenge.

## Results
Coming soon.
The population graph has been formed, but the district forming algorithm is still in progress.

An example starting graph of Michigan:
![Michigan](https://content.screencast.com/users/ChrisLars/folders/Snagit/media/d367613e-19c3-40ff-9ef6-37483836da5e/11.08.2018-07.07.png)

Start of the Forest Fire fill to find district candidates to feed the recursive splitting (even split of the state here) sorting by compactness:
![Michigan Forest Fire Fill Even Split](https://content.screencast.com/media/cef9f5d8-9235-4af6-9b5b-c7607a913d1c_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_2018-11-10_23-13-52.png)

A complete Forest Fire fill with contiguous bugs
![Buggy Fill](https://content.screencast.com/media/e8a18583-9de2-42d3-9270-d07455192807_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_2018-11-11_09-45-36%20copy.png)


## Notes
Notice that we are only using population maps to create the district maps

[Third Party Licensing](ThirdPartyLicensing.md)
