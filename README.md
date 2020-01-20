# gap_jumper
You want to directly cross from one spiral arm of the galaxy to another but there is this giant gap between them? This program helps you to find a way.

## Problem:  
You are an explorer in Elite: Dangerous und you are out there in the endless void. In a region with a really low star density. And you seem not to be able to find a way out of there (or to the other side) and you have just some few materials left to boost your jumps?

## Solution:  
Well, most likely you are treading on the path's of the ancients. Use their knowledge to your advantage. It is all available on the number one place to go for all exploration related information: EDSM. 
They have nigthly dumps of their database which contains information of all the star systems the community has discovered so far.

## What you'll get
This python 3 program uses these databases (which one is described below) to find stars to jump to between the system you are in (or near) right now and the system you want to jump to.
The program is NOT designed to find the shortest path, but the most economic path, needing the fewest boosted jumps possible.
Just put the necessary information (start- and end-coordinates, your jump-ranges and a bit more) at the beginning of the < gap_jumper.py > file and then call the same on the command-line.

# Usage
If you are a windows user and don't want to run the code yourself: simply double click the exe-file. This will start the GUI.

If you want to run the code yourself (recommended) simply call python 3 on a shell/bash/console with the program name as a parameter:
```
$ python3 gap_jumper.py
```
That will start the GUI, too. It is assumed that all necessary modules are installed. It is also assumed that users who run the code themself know how to do that.

Provide the necessary input and press continue. Press the buttons from top to bottom on the next screen. Because the pathfinding algorithm can't start before the necessary isn't provided about the relevant stars between start- and end-point. The necessary information about the relevant stars can't be provided before these are actually found in the database.

An option for looking up the necessary stars online at EDSM is available. However, I recommend to use the offline mode due to server side rate limits (see below). For that the `systemsWithCoordinates.json.gz` from [EDSM Nightly Dumps](https://www.edsm.net/en/nightly-dumps) needs to be downloaded and the unzipped (!) file must be copied into the local directory (the same directory as the code/exe-file(s)). 

If neutron boosting shall be used the neutron star information will be downloaded automatically from [edastro.com](https://edastro.com/mapcharts/files/neutron-stars.csv).

During each run, the data for the set of stars considered is cached in the local directory. When the "Used cached stars"-option is chosen, this file is taken instead of querying EDSM or attempting to open the systemsWithCoordinates.json file. This is much faster if you want to adjust your search parameters within the same region of space.

# ATTENTION
All of the necessary steps need quite some time. And the more stars that need to be considered the more time is needed. But the void is patient.

Note that EDSM enforces rate limits. When fetching stars in the default online mode, this program sends API queries as fast as possible without exceeding the limits. This works out to fetching about 360 requests unthrottled, and one request per ten seconds after that. In terms of the algorithm implemented here, routes of up to about 2000 LY will be fetched unthrottled. Beyond 2000 LY, the throttling means each additional 200 LY will add about 5 minutes.

For comparison, the ~1.5 GB `systemsWithCoordinates.json.gz` file can be downloaded over a fast link in about one hour. Thus if you need to plot more than 6-7000 LY, you may be better off downloading the full dataset. However, for such long routes, until the algorithm is further optimized, the time spent computing the route may exceed the download time anyway.

Discussion of this program, and further description of the motivations and approach, can be found in the Frontier Forum thread: [The ancient automated pathfinder-stations](https://forums.frontier.co.uk/threads/the-ancient-automated-pathfinder-stations.475668/). Additional information can be found in the source code comments.
