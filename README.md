
https://medium.com/@larson.chris/a-new-redistricting-algorithm-redistricting-michigan-b29fab46511a

# Usage
There are three methods that should be called. I’ve run this through an IDE, so there aren’t any Python arguments to run from Python’s Interpreter just yet. But there are three main files that need to be run:
### censusData/getBlockData.py
Gets all the block data from the US Census Department for a state.

### formatData/formatBlockData.py
Formats the data in a way that forms a graph.

### district/createDistricts.py
Creates and exports the maps based on parameters in that file.

It’s all coded to create Federal Congressional maps for Michigan at the moment.

# Redistricting
Fair US state redistricting experiments without using demographic info beyond location.

## The problems

#### Not every vote is equal
Using Michigan as an example. In the 2012 election (after the last round of redistricting), these were the congressional election results statewide:

|                    | Republican | Democratic |
|——————————|——————|——————|
| Seats won          | 9          | 5          |
| Total vote         | 2,086,804  | 2,327,985  |
| Percentage of vote | 45.62%     | 50.89%     |

[Data taken from Wikipedia](https://en.wikipedia.org/wiki/United_States_House_of_Representatives_elections_in_Michigan,_2012)

It certainly doesn’t look correct that Democratic candidates could have been voted for in stronger numbers, but won 4 fewer seats. These voters aren’t being accurately represented in Congress. 

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

Further, if they are given maps from outside the commission, they could approve maps that appear to be fair currently but won’t be in a few years. There have been advances in data collection and analysis that make it possible to create gerrymandered maps based on predicting population aging and migrations.

#### Make all districts competitive
When most people discuss competitive voting districts, they are referring to districts that have close to the same number of Democrats and Republicans. There are some problems with this.
* It further ingrains just those two parties into our political system
* At what cost do we create competitive districts? If people choose to live with like-minded individuals, that’s their choice.
   * This is an attempt to remove unnatural non-competitiveness. Not combat the so-called [Big Sort](http://www.thebigsort.com/home.php).
   
#### Other population distribution algorithms
These are similar to this experiment’s proposed solution. They all eliminate any bias that may arise when using demographic data, which makes them good solutions in their own right. But there are still some issues with each that can be addressed.

##### Shortest-splitline
[The rules of this algorithm](https://en.wikipedia.org/wiki/Gerrymandering#Shortest_splitline_algorithm) use only the population distribution and geographic shape of the state to create district maps.

But problems arise when finding districts in densely populated urban areas. It tends to break them up indiscriminately. [Examples can be found here.](https://rangevoting.org/SplitLR.html)

##### Shortest average distance to center
This algorithm uses US Census blocks to creates districts where people have the lowest average distance to the center of their district.

As far as I understand this method (correct me if I’m wrong): The primary advantage of this method is that it creates fairly round and compact districts. Which the shortest travel times for constituents. It still has the same problem of potentially breaking up larger populations. That is mitigated by an element of randomness, which leads to a human choosing from a result set for the best maps. This introduces some bias into the system.

[A great explanation of the process can be found here.](https://bdistricting.com/about.html)

## Proposed Solution
Evenly split a state into a set number of districts by using county lines and population borders while keeping districts as compact as possible. Splitting is done by finding the lowest population paths through each county.

### Rules the method will follow

#### Keep communities together
By using the [2010 US Census data](https://www2.census.gov/census_2010/04-Summary_File_1/Michigan/), this experiment will break up each state (starting with Michigan) into individual census blocks (the smallest population Census unit). With those blocks, form a population density map where each Census block knows its nearest neighboring blocks. Forming a state-wide population graph, in which the method initially splits the state using county lines.

Further splits will use a form of [dynamic programming used in seam carving](https://en.wikipedia.org/wiki/Seam_carving#Dynamic_programming)(an image analyzing method used for content-aware resizing). By finding the lowest population path through a group of Census blocks, it will avoid breaking apart communities.

Ideally by doing this, maps will naturally comply with the Voting Rights Act, but as mentioned before, using demographics other than location can lead to bias. So this experiment won’t be using any of that information. And will leave the evaluation of the maps under the Voting Rights Act to third parties after map creation. 

#### Use of population borders
The algorithm starts with state county borders, an already familiar set of dividing lines to most constituents. And then it will create its own split lines that will avoid population dense areas or communities. The smallest possible population group will be Census blocks.

#### Keep districts as round or compact as possible
Originally the method attempted to use the [Polsby-Popper Test](https://en.wikipedia.org/wiki/Polsby-Popper_Test) when forming a district, it would assign a weight to each group of blocks. And then choose which block was next by finding the group of blocks by finding the largest Polsby-Popper value. But this caused the algorithm to avoid lakeside counties due to the complexity of the shoreline. Seen here:

![Polsby-Popper Forest Fire Fill](https://content.screencast.com/media/944eee16-1600-42ea-8e63-7a0fbbe1aefc_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_Forest%20Fire%20Fill%20-%20Michigan%20-%20Even%20Split.gif)

And then it used a simple distance from center comparison. So it choose the closest groups of blocks to form compact districts:

![Distance Weighted Forest Fire Fill](https://content.screencast.com/media/42621953-e940-4139-a6b9-40fcb62ab38a_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_DistanceWeight.gif)

But problem arose when districts got smaller. The best result so far has been simply filling north to south or west to east. It chooses which direction based on the orientation of the geometry. For example, since the state of Michigan is taller than it is wide, it will start filling from the north:

![Cardinal Direction Weighted Forest Fire Fill](https://content.screencast.com/media/2c97a27f-cb17-4a97-b6b4-dcf6c0e04449_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_CardinalFillingBottomDistance.gif)

### Technical process
There are two main parts to this algorithm:
* Creating districts from a set of groups of Census blocks
* Breaking apart groups of Census blocks if the districts don’t meet compactness and population requirements.
(And the algorithm will repeat until the rules are met)

When attempting to create districts, it recursively splits the state into districts of appropriately sized ratios and stops when the desired number of districts are created. The recursive splitting based on ratios is similar to the [shortest-splitline](#Shortest-splitline) method. But instead of trying to find a dividing line, it uses a [Forest Fire algorithm](https://en.wikipedia.org/wiki/Flood_fill#Alternative_implementations) to find candidate groups that most closely match the desired population ratio. As mentioned above, the Forest Fire fill is weighted by filling north to south or west to east.

Example:
![Cardinal Direction Weighted Forest Fire Fill](https://content.screencast.com/media/726be446-97f6-40ac-a5dc-dba2c13ba66b_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_NewCardinal.gif)
*A weighted forest fire fill attempting to split the state of Michigan in half by population. Blue groups are part of the proposed fill. Green is the next best candidate based on the compactness value. And orange groups are potentially isolated groups (districts must be contiguous).*

If the population ratio cannot be met or the resulting district split doesn’t meet a roundness threshold, a selection of groups are split via the method of [dynamic programming used in seam carving](https://en.wikipedia.org/wiki/Seam_carving#Dynamic_programming) that has been mentioned above.

Example of the population energy heatmap used for splitting up a group:
![Directional Heatmap](https://content.screencast.com/media/2993b050-e3ce-4add-b39b-50c5dea31976_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_SeamFindingEastToWest.gif)
Drawn from west to east. To find a sensible split, the method takes the values along the eastern border and work our way back to the western border, finding the least energetic neighbor along the way to find the least disruptive path.

Here is an example of finding a low population energy seam working from south to north:
![Finding seam with south to north](https://content.screencast.com/media/3e9fe534-1be7-44e4-a498-8bf8333a60d5_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_SeamFindingSouthToNorth.gif)

### Problems
There are some rough edges in highly populated areas:
![Rough edges in Detroit](https://content.screencast.com/media/a913585e-cb52-4162-8072-60ef52ea3270_9e007f70-eddf-41a3-994c-9b412edca7cd_static_0_0_2018-12-31_10-56-55.png)

This should be addressable by 

## Results
Coming soon.
The population graph has been formed, but the district forming algorithm is still in progress. **The examples shown below are just with a weighted Forest Fire fill and still need the split method mentioned above.**

An example starting graph of Michigan:
![Michigan](https://content.screencast.com/users/ChrisLars/folders/Snagit/media/d367613e-19c3-40ff-9ef6-37483836da5e/11.08.2018-07.07.png)

Start of the Forest Fire fill to find district candidates to feed the recursive splitting (even split of the state here) sorting by compactness:
![Michigan Forest Fire Fill Even Split](https://content.screencast.com/users/ChrisLars/folders/Snagit/media/b95e9430-a0f6-4583-9365-f564ec89c5ad/11.15.2018-06.55.png)

A complete Forest Fire fill without breaking up counties (This is next):
![Forest Fire Fill - No Breaking](https://content.screencast.com/users/ChrisLars/folders/Snagit/media/e4ce9633-7523-4a81-b0f1-8e33e4a277f9/11.15.2018-06.43.png)

# Notes
Notice that the method is only using population maps to create the district maps

[Third Party Licensing](ThirdPartyLicensing.md)
