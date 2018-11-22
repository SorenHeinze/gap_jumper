#    "gap_jumper" (v1.0)
#    Copyright 2018 Soren Heinze
#    soerenheinze (at) gmx (dot) de
#    5B1C 1897 560A EF50 F1EB 2579 2297 FAE4 D9B5 2A35
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This program is meant to be used to find a possible path in regions with 
# extremely low star density. It takes the EDSM star-database and finds a way 
# from a given start- to a given end-point. If the spaceship can do it at all, 
# that is.
# 
# The route is NOT necessarily the shortest way, because highest priority was 
# set to save as much materials as possible by using boosted jumps just if no 
# other way can be found.
# 
# ATTENTION: Finding the information can take some time. Ca. one hour on my 
# 2012 laptop.
# ATTENTION: You may imagine that it is probably not a good idea to run this
# program in regions with high (or even regular) star density. But who am 
# I to restrict your possibilities? 

import class_definitions as cd
import additional_functions as af
import pickle


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ##   Input information below  ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

# start- and end-coordinates from in-game starmap
# Below you can see an example
start_coords = {'x': 16602.0, 'y': -0.0, 'z': -10460.0}
end_coords = {'x': 14550.0, 'y': -0.0, 'z': -7550.0}

# The distances the spaceship can jump.
# 
# ATTENTION: The very first value MUST be zero!
# ATTENTION: every second value is the jump distances on fumes, for the given 
# boost level.
# So it needs to look like this:
# [0, boost_0_jump, boost_0_jump_on_fumes, boost_1_jump, boost_1_jump_on_fumes ... ]
# Below you can see an example for an Anaconda.
jumpable_distances = [0, 71.33, 73.73, 89.16, 92.16, 107.0, 110.59, 142.66, 147.45]

# Number of tries to find the best path.
# Use 1000 to be really sure, but sth. like 23 should give you results which 
# are not too far away from the most economic or fewest jumps route.
max_tries = 23

# The path with the star database-files.
path = ''

# File with the star coordinates.
# The data can be downloaded here: https://www.edsm.net/en/nightly-dumps
coordinates_file ='systemsWithCoordinates.json'

# File with additional information about celestial bodies.
# The data can be downloaded here: https://www.edsm.net/en/nightly-dumps
additional_information_file = 'bodies.json'


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##  Outcomment below if the stars for  ## ## ##
## ## ## ##  a new path shall be found for the  ## ## ## 
## ## ## ##  first time.                        ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

#filename = path + 'one_way_more_information'
#with open(filename, 'rb') as f:
	#stars = pickle.load(f)


#filename = path + 'all_nodes'
#with open(filename, 'rb') as f:
	#pristine_nodes = pickle.load(f)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##  Outcomment above if the stars for  ## ## ##
## ## ## ##  a new path shall be found for the  ## ## ## 
## ## ## ##  first time.                        ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##



## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##  REMOVE comments below if the stars ## ## ##
## ## ## ##  for a new path shall be found for  ## ## ## 
## ## ## ##  the first time.                    ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

infile = path + coordinates_file
stars = af.find_systems(start_coords, end_coords, infile)

filename = path + 'one_way'
with open(filename, 'wb') as f:
	pickle.dump(stars, f)


infile = path + additional_information_file
af.find_additional_information(stars, infile)

filename = path + 'one_way_more_information'
with open(filename, 'wb') as f:
	pickle.dump(stars, f)


pristine_nodes = af.create_nodes(stars, jumpable_distances)

filename = path + 'all_nodes'
with open(filename, 'wb') as f:
	pickle.dump(pristine_nodes, f)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##  REMOVE comments above if the stars ## ## ##
## ## ## ##  for a new path shall be found for  ## ## ## 
## ## ## ##  the first time.                    ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##



start_star, end_star = af.find_closest(stars, start_coords, end_coords)

most_economic_jumper, fewest_jumps_jumper = af.find_path(max_tries, stars, \
											start_star, end_star, pristine_nodes)

print()
print("Start at: ", start_star)
print("  End at: ", end_star)
print("\nNumber of stars considered: ", len(stars))

af.print_jumper_information(pristine_nodes, most_economic_jumper, fewest_jumps_jumper)






















