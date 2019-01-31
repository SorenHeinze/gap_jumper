# gap_jumper
You want to directly cross from one spiral arm of the galaxy to another but there is this giant gap between them? This program helps you to find a way.

## Problem:  
You are an explorer in Elite: Dangerous und you are out there in the endless void. In a region with a really low star density. And you seem not to be able to find a way out of there (or to the other side) and you have just some few materials left to boost your jumps?

## Solution:  
Well, most likely you are treading on the path's of the ancients. Use their knowledge to your advantage. It is all available on the number one place to go for all exploration related information: EDSM. 
They have nigthly dumps of their database which contains information of all the star systems the community has discovered so far.

## What you'll get
This python 3 program uses two of these databases (which one is described in the source-code) to find stars to jump to between the system you are in (or near) right now and the system you want to jump to.
The program is NOT designed to find the shortest path, but the most economic path, needing the fewest boosted jumps possible.
Just put your information (start- and end-coordinates and your jump-ranges) at the beginning of the < gap_jumper.py > file and then call the same on the command-line.

## ATTENTION
The search in the database is inefficient and will take some time. But the void is patient.

The most up to date version does not require to download these databases any longer but uses the EDSM API to get the needed information. However, due to certain limitations does the program need to make quite a lot of requests and there seems to be a limit how many one can make.
So, this feature is to be considered untested.
I may provide at a later version the ability to either use the API or the downloaded database.
