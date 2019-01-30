#    "additional_functions" (v1.0)
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

# This file contains functions used in AA_gap_jumper.py which could not go 
# into either the Node-class or the Jumper-class.

import class_definitions as cd
from math import sqrt
from copy import deepcopy
from random import shuffle
import json
import requests

# Problem that may occur: No jumps take place because all possible jumps
# go to unscoopble stars, the jumper has just one jump left and within
# one regular jump distance no scoopable star is available. The latter 
# would have been checked already in node._check_free_stars().
# BUT, it may be possible that a scoopable star exists two (or more) jumps 
# away.
# All these possibilities could not be implemented in the regular code.
# Solution: Take the possibility of the later into account by giving the 
# jumper fuel fo one additional jump so that it can cross the gap to the 
# next (unscoopable) star and hope that after that a star exists that can be 
# used for refill.
# 
# I think that this function will actually never be called.
def refuel_stuck_jumpers(all_nodes):
	for starname, node in all_nodes.items():
		jumper = node.jumper
		# This shall be done just for jumpers with an almost empty tank.
		# The main while loop has, at the point when this function is called,
		# already checked for each jumper and all distances if it is possible 
		# to jump to a star and obviously failed to find one for all jumpers.
		# If it is because of the case described above, giving these jumpers
		# fuel for another jump should solve this problem and when calling 
		# said main loop again it should find a star to jump to, if there is 
		# one.
		if jumper and jumper.jumps_left == 1:
			jumper.jumps_left = 2
			jumper.magick_fuel_at.append(node.name)
			this = 'ATTENTION: needed magick re-fuel at {} to be '.format(node.name)
			that = 'able to jump. You need to get there with at least 2 jumps left! '
			siht = 'Otherwise you are stuck at the next star!'
			jumper.notes.append(this + that + siht)



# This finds the closest system to a given point. Used to find the 
# systems closest to the start- and end-coords.
def distance_to_point(point_1_coords, point_2_coords):
	x_0 = point_2_coords['x']
	y_0 = point_2_coords['y']
	z_0 = point_2_coords['z']

	x_1 = point_1_coords['x']
	y_1 = point_1_coords['y']
	z_1 = point_1_coords['z']

	distance_to_point = sqrt((x_1 - x_0)**2 + (y_1 - y_0)**2 + (z_1 - z_0)**2)

	return distance_to_point



# Things that are needed to find a point on the line between the start- and 
# the end-coords.
def calculate_line_stuff(start_coords, end_coords):
	x_ = end_coords['x'] - start_coords['x']
	y_ = end_coords['y'] - start_coords['y']
	z_ = end_coords['z'] - start_coords['z']

	distance = sqrt(x_**2 + y_**2 + z_**2)

	# < unit_vector > for the line from start- to end-coords.
	unit_vector = {}
	unit_vector['x'] = x_ / distance
	unit_vector['y'] = y_ / distance
	unit_vector['z'] = z_ / distance

	start_of_line = {}
	start_of_line['x'] = start_coords['x'] - 400 * unit_vector['x']
	start_of_line['y'] = start_coords['y'] - 400 * unit_vector['y']
	start_of_line['z'] = start_coords['z'] - 400 * unit_vector['z']

	end_of_line = {}
	end_of_line['x'] = end_coords['x'] + 400 * unit_vector['x']
	end_of_line['y'] = end_coords['y'] + 400 * unit_vector['y']
	end_of_line['z'] = end_coords['z'] + 400 * unit_vector['z']

	# I need two vectors perpendicular to the unit_vector (along the line) to 
	# be able to get the center-coords of the cubes along the line (see
	# comment in stars_in_cube).
	# I have just ONE vector, the unit_vector. Fortunately is the cross product 
	# between two vectors perpendicular to both. Thus I need just the second
	# vector. 
	# Fortunately (again), in 3D I just need to switch two "components"
	# add a minus to the second and set the third component to zero to get a 
	# vector perpendicular to the original vector. 
	# Example: 
	# vector = 3x + 4y + 5z
	# perpendicular = 4x - 3y + 0z
	# ATTENTION: Make sure that not both of the switched components are zero.
	perpendicular_vector_1 = {}
	if unit_vector['y'] != 0:
		first = unit_vector['y']
		second = -unit_vector['x']
		third = 0
	else:
		first = unit_vector['z']
		second = 0
		third = -unit_vector['x']

	# Don't forget to normalize.
	length = sqrt(first**2 + second**2 + third**2)
	perpendicular_vector_1['x'] = first / length
	perpendicular_vector_1['y'] = second / length
	perpendicular_vector_1['z'] = third / length

	# And now the cross product to get the second perpendicular vector.
	# Since the former two are already normalized, it will automatically have 
	# unit length.
	a_1 = unit_vector['x']
	a_2 = unit_vector['y']
	a_3 = unit_vector['z']

	b_1 = perpendicular_vector_1['x']
	b_2 = perpendicular_vector_1['y']
	b_3 = perpendicular_vector_1['z']

	perpendicular_vector_2 = {}
	perpendicular_vector_2['x'] = a_2 * b_3 - a_3 * b_2
	perpendicular_vector_2['y'] = a_3 * b_1 - a_1 * b_3
	perpendicular_vector_2['z'] = a_1 * b_2 - a_2 * b_1

	return unit_vector, perpendicular_vector_1, perpendicular_vector_2, start_of_line, end_of_line


# EDSM API can get me all stars in a cube with a side length of 1000 ly.
# Testing has shown that I need cubes with a side length of 500 ly to get 
# good results in regions with a really low star density.
# Thus I build such cubes (well almost cubes) by stacking smaller 5 x 5 x 5
# cubes on each other. 
# This is what happens here.
# Afterwards I move one cube length along the line and do the same. Stars
# that are "counted" again will be removed. But the latter two things are 
# taking place in find_systems() and extract_information().
def stars_in_cubes_perpendicular_to_line(center_coords, perpendicular_vector_1, \
															perpendicular_vector_2):
	url = 'https://www.edsm.net/api-v1/cube-systems'
	counter_1 = -2
	counter_2 = -2

	all_stars = []
	i = 0
	while counter_1 < 3:
		while counter_2 < 3:
			print(i) 
			i+= 1
			x_ = center_coords['x'] + 200 * counter_1 * perpendicular_vector_1['x'] + \
												200 * counter_2 * perpendicular_vector_2['x']
			y_ = center_coords['y'] + 200 * counter_1 * perpendicular_vector_1['y'] + \
												200 * counter_2 * perpendicular_vector_2['y']
			z_ = center_coords['z'] + 200 * counter_1 * perpendicular_vector_1['z'] + \
												200 * counter_2 * perpendicular_vector_2['z']

			payload = {'x':x_, 'y':y_, 'z':z_, 'size':200, 'showCoordinates':1, \
																'showPrimaryStar':1}
			systems = requests.get(url, params = payload)
			all_stars.append(systems.json())

			counter_2 += 1

		counter_1 += 1
		counter_2 = -2

	return all_stars


# Of all the information returned by stars_in_cubes_perpendicular_to_line()
# I need JUST the things processed in this function
# < stars > is a dict which contains each systems information between start- 
# and end-coords in the given corridor of stacked cubes as returned by 
# stars_in_cubes_perpendicular_to_line().
def extract_information(stars, this_section_stars):
	for element in this_section_stars:
		# An element in this_section_stars can be a list with one or
		# more dicts or an empty dict.
		if len(element) > 0:
			for this_dict in element:
				starname = this_dict['name']
				coords = this_dict['coords']
				scoopable = this_dict['primaryStar']['isScoopable']

				stars[starname] = {}
				stars[starname].update(coords)
				stars[starname]['scoopable'] = scoopable

	return stars


# This does all of the above.
# < start_coords > and < end_coords > are dicts with the (approximate) 
# coordinates of the star at the start and the star at the end.
def find_systems(start_coords, end_coords, infile):
	# < unit_vector > is for the line from start- to end-coords.
	unit_vector, perpendicular_vector_1, perpendicular_vector_2, start_of_line, \
		  end_of_line = calculate_line_stuff(start_coords, end_coords)

	stars = {}
	center_coords = start_of_line
	# Due to float and rounding errors can I not set the break condition 
	# directly to reaching the end_of_line. However, the worst difference can 
	# maximaly be 100 ly, which is a value I can live with, since end_of_line
	# is already 500 ly away from end_coords.
	# I use a high number here and not the actual distance for the very first 
	# loop, so that (very) short routes are covered, too.
	difference = 99999999
	while difference > 100:
		difference = distance_to_point(center_coords, end_of_line)

		this = "Getting all systems between start and end "
		that = "(distance = {} ly). This will take some time...".format(int(difference))
		print(this + that)

		this_section_stars = stars_in_cubes_perpendicular_to_line(center_coords, \
										perpendicular_vector_1, perpendicular_vector_2)
		print(this_section_stars)
		stars = extract_information(stars, this_section_stars)

		center_coords['x'] = center_coords['x'] + 200 * unit_vector['x']
		center_coords['y'] = center_coords['y'] + 200 * unit_vector['y']
		center_coords['z'] = center_coords['z'] + 200 * unit_vector['z']

		print(stars)
	return stars



# The start- and endpoint are likely unknown stars or just approximate 
# coordinates from the ingame starmap. This function finds the actual 
# (known) stars which are closest to the given positions.
def find_closest(stars, start_coords, end_coords):
	start_distance = 9999999999999.0
	end_distance = 9999999999999.0

	start_star = None
	end_star = None

	for star_name, star_coords in stars.items():
		distance_to_start = distance_to_point(start_coords, star_coords)
		distance_to_end = distance_to_point(end_coords, star_coords)
		if distance_to_start < start_distance:
			start_distance = distance_to_start
			start_star = {star_name:star_coords}

		if distance_to_end < end_distance:
			end_distance = distance_to_end
			end_star = {star_name:star_coords}

	return start_star, end_star



# This takes in all the star-data and creates node-object.
def create_nodes(stars, jumpable_distances):
	all_nodes = {}
	i = 0 
	for starname, data in stars.items():
		node = cd.Node(starname, data, jumpable_distances, stars, all_nodes)
		all_nodes[starname] = node

	return all_nodes



# A jumper needs to be initialized in the startnode.
def create_jumper_at_start(start_star, all_nodes):
	starname = list(start_star.keys())[0]
	jumper = cd.Jumper(starname, 4)

	all_nodes[starname].jumper = jumper
	all_nodes[starname].visited = True


# Problem: 
# 1.: Assume no regular jumps are possible. Thus this_distance in explore_path()
# will be set to 1 (or 2 etc.) for ALL stars.
# 2.: From star A to star B a boosted jumps take place. Star B contains now
# a jumper.
# 3.: If star B has NOT been "called" in the while loop in explore_path() 
# it will be "called" after star A had sent a jumper to it. However, 
# this_distance is still NOT set back to zero. Thus, the jumper at star B 
# jumps now ALSO a boosted jump to star C.
# 
# This leads to more boosted jumps than absolute necessary. An extreme case I 
# had once were ver 5 grade three boosted jumps over 600 ly instead of one
# grade three boosted jumps at the place where it was necessary and just regular 
# jumps afterwards.
# 
# Solution: if this_distance != 0 allow jumps JUST from stars that have 
# free stars in their vicinity.
# This is what this function takes care of.
def get_nodes_that_can_send_jumpers(all_nodes, this_distance):
	starnames = []
	for starname, node in all_nodes.items():
		if node.jumper:
			node._check_free_stars(this_distance)
			if len(node.can_jump_to) != 0:
				starnames.append(starname)

	return starnames


# This does all the above and finds a way from start to end (or not).
def explore_path(all_nodes, stars, final_node):
	# This is the index of the possible jump distances in the 
	# jump_distances-attribute of the Node-class. The initial index must be 
	# zero.
	this_distance = 0
	magick_fuel = False
	while not final_node.visited:
		starnames = get_nodes_that_can_send_jumpers(all_nodes, this_distance)

		if len(starnames) == 0:
			this_distance += 1
			# When stuck, give (once) a magick re-fuel. Do this just again, if a
			# jump occured after the magick re-fuel.
			# Due to many stars not having information about scoopability I had
			# to set the default value of this attribute to True. Thus, I think
			# that this if-condition will never be triggered.
			if this_distance == len(final_node.reachable) and not magick_fuel:
				magick_fuel = True
				this_distance = 0
				print("BEFORE")
				refuel_stuck_jumpers(all_nodes)
				print("AFTER")

			elif this_distance == len(final_node.reachable):
				# If no way can be found even with the largest boost range, and
				# even after ONE magick fuel event took place, break the loop.
				break
		else:
			# I will run explore_path to find the best way. However, it seems to be
			# that once the program is called, that .items() returns the items
			# always in the same order. Thus explore_path() will return always
			# the same path. This is avoided by shuffling.
			shuffle(starnames)

			for starname in starnames:
				node = all_nodes[starname]
				node._send_jumpers(this_distance)

			this_distance = 0
			# If a jump is possible after a magick fuel event, everything can
			# be done as before. This includes that after the jump more magick 
			# fuel events can take place. Yes, that means that a route may be just 
			# possible if magickally fuelled all the way.
			magick_fuel = False



# This function takes the points of a route and tries to figure out if there 
# are jumps that could have been avoided. E.g., instead of jumping 1 => 2 => 3
# if a direct jump 1 => 3 would have been possible.
# If yes, the unnecessary step will be deleted.
# However, all of this is done just within regular jump distance.
# 
# ATTENTION: After some testing it turned out that the original algorithm is 
# already really good. The difference between running this function or not was
# never larger than 1 jump. Thus I decided not to use it.
# However, I think that it may be useful to have in the future, thus I keep it.
def find_more_direct_way(final_node, all_nodes):
	visited = deepcopy(final_node.jumper.visited_systems)
	jump_types = deepcopy(final_node.jumper.jump_types)

	i = 0
	length = len(visited)
	while i < length - 1:
		starname = visited[i]
		node = all_nodes[starname]

		# Since visited is an ordered list, can I just check if a star further 
		# away but within regular jump range
		j = i + 2
		while j < length:
			try_to_jump_to = visited[j]
			if try_to_jump_to in node.reachable[0]:
				del visited[j - 1]
				del jump_types[j - 1]
				length -= 1
				j -= 1
			j += 1
		i += 1

	final_node.jumper.visited_systems = visited
	final_node.jumper.jump_types = jump_types



# Just to print the complete path information in a pretty way.
def pretty_print(pristine_nodes, jumper):
	for i in range(len(jumper.visited_systems)):
		starname = jumper.visited_systems[i]
		jump_type = jumper.jump_types[i]
		distance = round(jumper.distances[i], 2)

		node = pristine_nodes[starname]
		scoopable = node.data['scoopable']
		x_ = node.data['x']
		y_ = node.data['y']
		z_ = node.data['z']

		this = '{}\t{}\t{}\t'.format(starname.replace(' ', '_'), distance, jump_type)
		that = '{}\t{}\t{}\t{}'.format(scoopable, x_, y_, z_)
		print(this + that)



# This function figures out if the jumper that reached the final node during 
# the current loop uses less jumps or less boosts than the current best jumper.
# < data > is a tuple that contains information from the previous jumps
def better_jumper(i, max_tries, jumper, data):
	fewest_jumps_jumper = data[0]
	fewest_jumps = data[1]
	level_3_boosts = data[2]
	level_2_boosts = data[3]
	level_1_boosts = data[4]

	new_level_3_boosts = len([x for x in jumper.jump_types if '3' in x])
	new_level_2_boosts = len([x for x in jumper.jump_types if '2' in x])
	new_level_1_boosts = len([x for x in jumper.jump_types if '1' in x])
	number_jumps = len(jumper.visited_systems)

	this = 'Try {} of {}. '.format(i + 1, max_tries)
	that = 'Did {} jumps with {} level 3 boosts, '.format(number_jumps, \
																new_level_3_boosts)
	siht = '{} level 2 boosts, {} level 1 boosts'.format(new_level_2_boosts, \
																new_level_1_boosts)
	print(this + that + siht)

	if number_jumps < fewest_jumps and new_level_3_boosts <= level_3_boosts and \
									new_level_2_boosts <= level_2_boosts and \
									new_level_1_boosts <= level_1_boosts:
		fewest_jumps = number_jumps
		fewest_jumps_jumper = jumper

		level_1_boosts = new_level_1_boosts
		level_2_boosts = new_level_2_boosts
		level_3_boosts = new_level_3_boosts

	data = (fewest_jumps_jumper, fewest_jumps, level_3_boosts, level_2_boosts, \
																	level_1_boosts)

	return data



# This is the main loop, that will search for the shortest and for the most 
# economic path as often as < max_tries >.
def find_path(max_tries, stars, start_star, end_star, pristine_nodes):
	final_name = list(end_star.keys())[0]
	fewest_jumps_jumper = None
	fewest_jumps = 99999
	level_3_boosts = 99999
	level_2_boosts = 99999
	level_1_boosts = 99999

	# This is just to keep the list of parameters for better_jumper() short.
	data = (fewest_jumps_jumper, fewest_jumps, level_3_boosts, level_2_boosts, \
																	level_2_boosts)

	i = 0
	while i < max_tries:
		# After one loop all nodes are visited. Thus I need the "fresh", 
		# unvisited nodes for each loop.
		all_nodes = deepcopy(pristine_nodes)
		create_jumper_at_start(start_star, all_nodes)
		final_node = all_nodes[final_name]

		explore_path(all_nodes, stars, final_node)

		if final_node.visited:
			jumper = final_node.jumper
		else:
			jumper = None

		if jumper:
			data = better_jumper(i, max_tries, jumper, data)
		else:
			print('Try {} of {}. Could NOT find a path.'.format(i, max_tries))

		i += 1

	fewest_jumps_jumper = data[0]

	return fewest_jumps_jumper


# To print the information about the pat in a good way.
def print_jumper_information(pristine_nodes, fewest_jumps_jumper):
	if fewest_jumps_jumper:
		print()
		number_jumps = len(fewest_jumps_jumper.visited_systems)
		level_3_boosts = len([x for x in fewest_jumps_jumper.jump_types if '3' in x])
		level_2_boosts = len([x for x in fewest_jumps_jumper.jump_types if '2' in x])
		level_1_boosts = len([x for x in fewest_jumps_jumper.jump_types if '1' in x])

		that = '{} => {}, {}, {}'.format(number_jumps, level_3_boosts, \
													level_2_boosts, level_1_boosts)
		print("fewest jumps: ", that)

		print()
		input("Below is a list of ALL stars visited (press ENTER): ")
		pretty_print(pristine_nodes, fewest_jumps_jumper)
	print()






















