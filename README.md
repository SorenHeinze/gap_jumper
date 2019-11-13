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

```
$ python gap_jumper.py -h
usage: gap_jumper.py [-h] [-v] --range LY [--range-on-fumes LY]
                     --startcoords X Y Z --destcoords X Y Z
                     [--cached] [--starsfile FILE] [--max-tries N]

You want to directly cross from one spiral arm of the galaxy to
another but there is this giant gap between them? This program helps
you to find a way. Default behavior is to use the EDSM API to load
stars on-demand. Use the --starsfile option if you have downloaded
the systemsWithCoordinates.json nigthly dump from EDSM.

optional arguments:
  -h, --help            show this help message and exit
  --range LY, -r LY     Ship range with a full fuel tank (required)
  --range-on-fumes LY, -rf LY
                        Ship range with fuel for one jump (defaults
                        equal to range)
  --startcoords X Y Z, -s X Y Z
                        Galactic coordinates to start routing from
  --destcoords X Y Z, -d X Y Z
                        Galactic coordinates of target destination
  --neutron-boosting bool, -nb bool
                        Utilize Neutron boosting. The necessary file 
                        will be downloaded automatically.
  --cached              Reuse nodes data from previous run
  --starsfile FILE      Path to EDSM system coordinates JSON file
  --max-tries N, -N N   How many times to shuffle and reroute before
                        returning best result (default 23)
  --verbose, -v         Enable verbose logging
```

## Examples

You will need to obtain the x/y/z galactic coordinates of your start and destination points. These can be obtained approximately from the in-game galaxy map, or by looking up a system name in EDSM. For these examples, let's consider a route from Beagle Point to Semotus Beacon.

  - Beagle Point: -1111.56 / -134.22 / 65269.75
  - Oevasy SG-Y d0 (Semotus Beacon): -1502.16 / -2.63 / 65630.17

Basic usage:

    python gap_jumper.py --range 60 --startcoords -1111.56 -134.22 65269.75 
        --destcoords -1502.16 -2.63 65630.17

The above invocation will query the EDSM API for the necessary system coordinates data and compute a route from the start to the destination for a ship with a 60 LY base range, using a minimum number of boosted jumps. 

Advanced usage:

    python gap_jumper.py -r 60 -rf 63.5 -s -1111.56 -134.22 65269.75 
        -d -1502.16 -2.63 65630.17 --starsfile /path/to/systems.json -N 40 -nb True

The above example uses the abbreviated options syntax. Here we specify a ship with base range of 60 LY and also specify a "range on fumes". The computed route will recommend reduced-fuel jumps when possible to save synth materials. Additionally, this example assumes that the `systemsWithCoordinates.json` file has been downloaded from [EDSM Nightly Dumps](https://www.edsm.net/en/nightly-dumps) as `systems.json`, 40 randomized attempts will be made to find an optimal route. In addition the file with the neutron star information will be downloaded from [edastro.com](https://edastro.com/mapcharts/files/neutron-stars.csv) and thus neutron boosts will be utilized (if possible).

During each run, the data for the set of stars considered is cached in the local directory. The option `--cached` makes use of this cache instead of querying EDSM or attempting to open the systems.json file. This is much faster if you want to adjust your search parameters within the same region of space.

# ATTENTION
The search in the database is inefficient and will take some time. But the void is patient.

Note that EDSM enforces rate limits. When fetching stars in the default online mode, this program sends API queries as fast as possible without exceeding the limits. This works out to fetching about 360 requests unthrottled, and one request per ten seconds after that. In terms of the algorithm implemented here, routes of up to about 2000 LY will be fetched unthrottled. Beyond 2000 LY, the throttling means each additional 200 LY will add about 5 minutes.

For comparison, the ~5 GB `systemsWithCoordinates.json` file can be downloaded over a fast link in around 2 hours. Thus if you need to plot more than 6-7000 LY, you may be better off downloading the full dataset. However, for such long routes, until the algorithm is further optimized, the time spent computing the route may exceed the download time anyway.

Discussion of this program, and further description of the motivations and approach, can be found in the Frontier Forum thread: [The ancient automated pathfinder-stations](https://forums.frontier.co.uk/threads/the-ancient-automated-pathfinder-stations.475668/). Additional information can be found in the source code comments, especially in 
