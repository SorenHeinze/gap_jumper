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

If you want to run the code yourself (recommended) it is assumed that all necessary modules are installed. It is also assumed that users who run the code themself know how to do that. Simply call python 3 on a shell/bash/console with the program name as a parameter:
```
$ python3 gap_jumper.py
```
That will start the GUI, too. 

You will see this window (well, the colour might be different):
![Image of User input window](https://github.com/SorenHeinze/gap_jumper/blob/master/0003_input_screen.png)

An option for looking up the necessary stars online at EDSM is available. However, I recommend to use the offline mode due to server side rate limits (see below). For that the `systemsWithCoordinates.json.gz` from [EDSM Nightly Dumps](https://www.edsm.net/en/nightly-dumps) needs to be downloaded and the unzipped (!) file must be copied into the local directory. The local directory is the same directory in which the running code (or the the exe-file) is residing. 

Provide the necessary input and press continue.  This will lead to the next screen (exampel with Neutron boosting activated):
![Image of User input window](https://github.com/SorenHeinze/gap_jumper/blob/master/0004_working_screen.png)

Press the buttons from top to bottom because the pathfinding algorithm can't start before the necessary information about the relevant stars between start- and end-point isn't provided. The necessary information about the relevant stars can't be provided before these are actually found in the database.

If neutron boosting shall be used the most current neutron star information will be downloaded automatically from [edastro.com](https://edastro.com/mapcharts/files/neutron-stars.csv) after the button marked "A" is pressed.  
Said button will not be shown if either this option wasn't chosen or if the file is up to date.

Pressing the button marked "B" finds the relevant stars between start- and end-point of the journey.  
During each run, the data for the set of stars considered is cached in the local directory. When the "Used cached stars"-option is chosen on the input screen, this file is taken instead of querying EDSM or attempting to open the systemsWithCoordinates.json file. This is much faster if you want to adjust your search parameters within the same region of space. In this case the button marked "B" will not be shown.  
Be aware, that finding the relevant stars takes some time. No matter if the search is conducted online or offline. This is the reason for the "Use cached stars" option.

Pressing the button marked "C" prepares the information from the previous step for the actual pathfinding algorithm.  
This process can take a lot of time if many stars (many more than approx. 10,000) need to be considered!

Finally, the process to find a path through the void is started by pressing the button marked "D".  
This process also takes a lot of time if many stars need to be considered.

Execution time of the last two process are reasonable if 10,000 stars or less are used. 13,000 stars are also ok; there is no strict limit. But e.g., 30,000 stars will likely lead to process-times beyond one hour.

The results will be shown in the text-field at the bottom of the screen.

# ATTENTION
All of the necessary steps need quite some time. And the more stars that need to be considered the more time is needed. But the void is patient.

The program is meant to be used in areas with a low star density, a.k.a. the edges of the galaxy (or probably between the spiral arms). DON'T use it in areas with moderate or high star density. Or well, you, the user, are free to do whatever you want to do. But if you do that, your memory will be gobbled up and structuring the information and the actual process of finding a path will take forever.

Note that EDSM enforces rate limits. When fetching stars in the online mode, this program sends API queries as fast as possible without exceeding the limits. This works out to fetching about 360 requests unthrottled, and one request per ten seconds after that. In terms of the algorithm implemented here, routes of up to about 2000 LY will be fetched unthrottled. Beyond 2000 LY, the throttling means each additional 200 LY will add about 5 minutes.

For comparison, the ~1.5 GB `systemsWithCoordinates.json.gz` file can be downloaded over a fast link in about one hour. Thus if you need to plot more than 6-7000 LY, you may be better off downloading the full dataset. 

Discussion of this program, and further description of the motivations and approach, can be found in the Frontier Forum thread: [The ancient automated pathfinder-stations](https://forums.frontier.co.uk/threads/the-ancient-automated-pathfinder-stations.475668/). Additional information can be found in the source code comments.
