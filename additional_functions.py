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



# This finds the closest system to a given startpoint
def distance_to_start(start_coords, star_coords, start_distance):
	x_0 = star_coords['x']
	y_0 = star_coords['y']
	z_0 = star_coords['z']

	x_1 = start_coords['x']
	y_1 = start_coords['y']
	z_1 = start_coords['z']

	distance_to_start = sqrt((x_1 - x_0)**2 + (y_1 - y_0)**2 + (z_1 - z_0)**2)

	if distance_to_start < start_distance:
		start_distance = distance_to_start

	return start_distance



# Dito for the endpoint.
def distance_to_end(end_coords, star_coords, end_distance):
	x_0 = star_coords['x']
	y_0 = star_coords['y']
	z_0 = star_coords['z']

	x_2 = end_coords['x']
	y_2 = end_coords['y']
	z_2 = end_coords['z']

	distance_to_end = sqrt((x_2 - x_0)**2 + (y_2 - y_0)**2 + (z_2 - z_0)**2)

	if distance_to_end < end_distance:
		end_distance = distance_to_end

	return end_distance



# Intuitively is the calculation of distance_within_500_Ly_from_line() more
# processing intensive than just checking if some values are larger or smaller
# to a given value.
# Hence, I check first if the stars are in a box of which the start and end 
# system (+ 500 Ly) define the walls. If this is the case 
# distance_within_500_Ly_from_line() will be called, too.
# 
# This function defines the limits of this box.
def x_y_z_limits(start_coords, end_coords):
	x_1 = start_coords['x']
	y_1 = start_coords['y']
	z_1 = start_coords['z']

	x_2 = end_coords['x']
	y_2 = end_coords['y']
	z_2 = end_coords['z']

	max_x = max(x_1, x_2) + 500
	max_y = max(y_1, y_2) + 500
	max_z = max(z_1, z_2) + 500

	min_x = min(x_1, x_2) - 500
	min_y = min(y_1, y_2) - 500
	min_z = min(z_1, z_2) - 500

	return (max_x, max_y, max_z), (min_x, min_y, min_z)



# Between the start- and endpoint a line exists. Don't take stars which are 
# more than 500 Ly away from this line. So I basically just want to have 
# stars in a tube from startpoint to endpoint with a diameter of 1000 Ly.
# 
# The number 500 seems to be a sweet point. Some testing revealed that 1000
# will lead to many more stars, but not significantly better results. Using
# 250 (or even less) results in very man boosted jumps, which are to be 
# avoided.
def distance_within_500_Ly_from_line(start_coords, end_coords, star_coords):
	x_0 = star_coords['x']
	y_0 = star_coords['y']
	z_0 = star_coords['z']

	x_1 = start_coords['x']
	y_1 = start_coords['y']
	z_1 = start_coords['z']

	x_2 = end_coords['x']
	y_2 = end_coords['y']
	z_2 = end_coords['z']

	# From here: http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
	first = (x_1 - x_0)**2 + (y_1 - y_0)**2 + (z_1 - z_0)**2

	numerator_1 = (x_1 - x_0) * (x_2 - x_1)
	numerator_2 = (y_1 - y_0) * (y_2 - y_1)
	numerator_3 = (z_1 - z_0) * (z_2 - z_1)

	numerator = (numerator_1 + numerator_2 + numerator_3)**2

	denominator = (x_1 - x_2)**2 + (y_1 - y_2)**2 + (z_1 - z_2)**2

	distance_squared = first - numerator / denominator

	if distance_squared <= 250000.0:
		return True



# This function checks for all stars if these are within the "box" (see 
# comment to x_y_z_limits()) and if this is the case it does the calculation 
# if the star in question is within the "tube" (see comment to 
# distance_within_500_Ly_from_line()).
# If both is the case True is returned.
def within_limits(max_limits, min_limits, start_coords, end_coords, data):
	x_ = data['coords']['x']
	y_ = data['coords']['y']
	z_ = data['coords']['z']

	# Oh yes that is right what's written here. I've figured by accident out 
	# that I actually can do it this way and I like it :) . 
	x_ok = min_limits[0] <= x_ and x_ <= max_limits[0]
	y_ok = min_limits[1] <= y_ and y_ <= max_limits[1]
	z_ok = min_limits[2] <= z_ and z_ <= max_limits[2]

	if x_ok and y_ok and z_ok:
		if distance_within_500_Ly_from_line(start_coords, end_coords, \
															data['coords']):
			return True
	else:
		return False



# This is just to keep find_systems() more tidy.
def get_star_into_dict(stars, start_coords, end_coords, \
											max_limits, min_limits, data):
	if within_limits(max_limits, min_limits, start_coords, end_coords, data):
		star_data = data['coords']
		star_data.update({'discoverer':None})
		star_data.update({'scoopable':None})

		stars[data['name']] = star_data



# This is just to keep find_systems() more tidy.
def create_data_from_line(line):
	# I need to read line for line, however, at the end of each line a 
	# < , > appears, which can not be read by json.loads().
	# Also are there whitespaces in the beginning. Hence, I first get 
	# rid of the latter and then ...
	foo = line.strip()
	# ... use the remaining information except for the very last comma.
	# ATTENTION: The very last entry does NOT have a comma at the end.
	# Hence, the if-condition here.
	if foo[-1] == ',':
		bar = foo[:(len(foo) - 1)]
	else:
		bar = foo

	return json.loads(bar)



# This does all of the above.
# < start_coords > and < end_coords > are dicts with the (approximate) 
# coordinates of the star at the start and the star at the end.
def find_systems(start_coords, end_coords, infile):
	max_limits, min_limits = x_y_z_limits(start_coords, end_coords)

	stars = {}

	i = 0
	with open(infile, 'r', encoding='utf-8-sig') as f:
		# DON'T READ THE COMPLETE FILE!!! THIS WILL RUIN YOUR DAY BY EATING 
		# UP ALL THE MEMORY!
		# Rather read it line for line and store just what is needed.
		for line in f:
			i += 1
			# I want to convert each line to a dict by using json.
			# However, since I'm not loading the complete file at once, some 
			# lines are not readable with json. Hence, I use "name" as a 
			# keyword to figure out if a line can be read.
			if 'name' in line:
				data = create_data_from_line(line)

				get_star_into_dict(stars, start_coords, end_coords, \
											max_limits, min_limits, data)

			# Just for information how far the calculation has become.
			if i % 1000000 == 0:
				print("checked star #{} ...".format(i))

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
		this_distance = distance_to_start(start_coords, star_coords, start_distance)
		that_distance = distance_to_end(end_coords, star_coords, end_distance)
		if this_distance < start_distance:
			start_distance = this_distance
			start_star = {star_name:star_coords}

		if that_distance < end_distance:
			end_distance = that_distance
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

	final_node = all_nodes[starname]



# This does all the above and finds a way from start to end (or not).
def explore_path(all_nodes, stars, final_node):
	# This is the index of the possible jump distances in the 
	# jump_distances-attribute of the Node-class. The initial index must be 
	# zero.
	this_distance = 0
	magick_fuel = False
	while not final_node.visited:
		jumped = False

		# I will run explore_path to find the best way. However, it seems to be
		# that once the program is called, that .items() returns the items
		# always in the same order. Thus explore_path() will return always
		# the same path. This is avoided by shuffling.
		starnames = list(stars.keys())
		shuffle(starnames)

		for starname in starnames:
			node = all_nodes[starname]
			jump_performed = node._send_jumpers(this_distance)

			# To continue with the loop it is enough if ONE jumper was send.
			# However if I use just the return value of _send_jumpers() one 
			# may set it to True and the next back to False. Thus the control 
			# parameter for continuing the while-loop (=> jumped) needs to be 
			# outside the for-loop, but be able to set within the latter. Thus 
			# I have jump_performed.
			if jump_performed:
				jumped = True

		if not jumped:
			this_distance += 1
			# When stuck, give (once) a magick re-fuel. Do this just again, if a
			# jump occured after the magick re-fuel.
			# Yes, this node is a "leftover" from the stuff happening above.
			# That doesn't matter, since this attribute is the same for all nodes.
			# Due to many stars not having information about scoopability I had
			# to set the default value of this attribute to True. This, I think
			# that this if condition will never be triggered.
			if this_distance == len(node.reachable) and not magick_fuel:
				magick_fuel = True
				this_distance = 0
				print("BEFORE")
				refuel_stuck_jumpers(all_nodes)
				print("AFTER")

			elif this_distance == len(node.reachable):
				# If no way can be found even with the largest boost range, and
				# even after ONE magick fuel event took place, break the loop ...
				break

		else:
			this_distance = 0
			# If a jump is possible after a magick fuel event, everything can
			# be done as before. This includes that after the jump more magick 
			# fuel events can take place. Yes, that means that a route may be just 
			# possible if magickally fuelled all the way.
			magick_fuel = False



# In a different database more information can be found about the stars.
# This database however, is much larger and thus I don't look into it, before
# I have all the possible stars on a path, which are considerably less than
# there are stars in the whole database.
def more_information_into_dict(stars, this_data):
	starname = this_data['systemName']

	# First, the discoverer of the main star.
	# 
	# ATTENTION: The dict with the information of a celestial body has no 
	# 'isMainStar' if it is not a star. However, this function should not be 
	# called if it isn't a star.
	if this_data['isMainStar']:
		# The dict may either not have 'discovery' or 'commander' as key, or the
		# value may be None, or the value may be "null", or the name contains
		# non-ascii characters. All have to be caught and handled. And nope! I 
		# will NOT struggle with stupid encoding errors. I've wasted enough 
		# time with that.
		try:
			discoverer = this_data['discovery']['commander']
		except (TypeError, KeyError) as error:
			discoverer = None
		# This should actually occur just when printing!
		except UnicodeEncodeError:
			discoverer = 'Someone with non-ascii characters in name. Check manually.'

		stars[starname]['discoverer'] = discoverer

	# Second, scoopability ... some comments:
	# 1.: Information about scoopability of a star is mostly not available and 
	# will be 1 by default. So I assume that most stars are scoopable. That is
	# highly questionable, but otherwise the algorithm will not work.
	# 2.: The main star of a system may not be scoopable but a sister star 
	# may be. Thus I check all stars in a given system and if just one is 
	# scoopable the whole node is considered scoopable.
	if stars[starname]['scoopable'] != True:
		stars[starname]['scoopable'] = this_data['isScoopable']



# This function looks in the other database if it can find the systems and
# gets additional information about it.
def find_additional_information(stars, infile):
	starnames = list(stars.keys())

	i = 0
	with open(infile, 'r', encoding='utf-8-sig') as f:
		for line in f:
			i += 1
			# See comment in find_systems() why i do this.
			if 'name' in line:
				data = create_data_from_line(line)

				if data['systemName'] in starnames and data['type'] == 'Star':
					more_information_into_dict(stars, data)

			if i % 1000000 == 0:
				print("checked entry #{} ...".format(i))



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
		discoverer = node.data['discoverer']
		scoopable = node.data['scoopable']
		x_ = node.data['x']
		y_ = node.data['y']
		z_ = node.data['z']

		this = '{}\t{}\t{}\t'.format(starname.replace(' ', '_'), distance, jump_type)
		try:
			that = '{}\t{}\t'.format(scoopable, discoverer.replace(' ', '_'))
		# NoneType has no attriute .replace()
		except AttributeError:
			that = '{}\t{}\t'.format(scoopable, discoverer)
		siht = '{}\t{}\t{}'.format(x_, y_, z_)
		print(this + that + siht)



# This function figures out if the jumper that reached the final node during 
# the current loop uses less jumps or less boosts than the current best jumpers.
# < data > is a tuple that contains information from the previous jumps
def better_jumper(i, max_tries, jumper, data):
	most_economic_jumper = data[0]
	fewest_jumps_jumper = data[1]
	fewest_jumps = data[2]
	level_3_boosts = data[3]
	level_2_boosts = data[4]
	level_1_boosts = data[5]

	new_level_3_boosts = len([x for x in jumper.jump_types if '3' in x])
	new_level_2_boosts = len([x for x in jumper.jump_types if '2' in x])
	new_level_1_boosts = len([x for x in jumper.jump_types if '1' in x])
	number_jumps = len(jumper.visited_systems)

	this = 'Try {} of {}. '.format(i + 1, max_tries)
	that = 'Did {} jumps with {} level 3 boosts, '.format(number_jumps, new_level_3_boosts)
	siht = '{} level 2 boosts, {} level 1 boosts'.format(new_level_2_boosts, new_level_1_boosts)
	print(this + that + siht)

	if number_jumps < fewest_jumps:
		fewest_jumps = number_jumps
		fewest_jumps_jumper = jumper

	# If the path with the fewest level 1 boosts is found during the two first
	# loops, it will not be found. I don't really care, since the differences
	# are not that big.
	if new_level_3_boosts < level_3_boosts:
		level_3_boosts = new_level_3_boosts
		most_economic_jumper = jumper
	elif new_level_2_boosts < level_2_boosts:
		level_2_boosts = new_level_2_boosts
		most_economic_jumper = jumper
	elif new_level_1_boosts < level_1_boosts:
		level_1_boosts = new_level_1_boosts
		most_economic_jumper = jumper

	data = (most_economic_jumper, fewest_jumps_jumper, fewest_jumps, level_3_boosts, level_2_boosts, level_1_boosts)

	return data



# This is the main loop, that will search for the shortest and for the most 
# economic path as often as < max_tries >.
def find_path(max_tries, stars, start_star, end_star, pristine_nodes):
	final_name = list(end_star.keys())[0]
	most_economic_jumper = None
	fewest_jumps_jumper = None
	fewest_jumps = 99999
	level_3_boosts = 99999
	level_2_boosts = 99999
	level_1_boosts = 99999

	# This is just to keep the list of parameters for better_jumper() short.
	data = (most_economic_jumper, fewest_jumps_jumper, fewest_jumps, level_3_boosts, level_2_boosts, level_2_boosts)

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

	most_economic_jumper = data[0]
	fewest_jumps_jumper = data[1]

	return most_economic_jumper, fewest_jumps_jumper


# To print the information about the pat in a good way.
def print_jumper_information(pristine_nodes, most_economic_jumper, fewest_jumps_jumper):
	if most_economic_jumper:
		print()
		number_jumps = len(most_economic_jumper.visited_systems)
		level_3_boosts = len([x for x in most_economic_jumper.jump_types if '3' in x])
		level_2_boosts = len([x for x in most_economic_jumper.jump_types if '2' in x])
		level_1_boosts = len([x for x in most_economic_jumper.jump_types if '1' in x])

		this = '{} => {}, {}, {}'.format(number_jumps, level_3_boosts, level_2_boosts, level_1_boosts)
		print("most economic: ", this)

		input("Below is a list of ALL stars visited (press ENTER): ")
		pretty_print(pristine_nodes, most_economic_jumper)
		print()

	if fewest_jumps_jumper:
		print()
		number_jumps = len(fewest_jumps_jumper.visited_systems)
		level_3_boosts = len([x for x in fewest_jumps_jumper.jump_types if '3' in x])
		level_2_boosts = len([x for x in fewest_jumps_jumper.jump_types if '2' in x])
		level_1_boosts = len([x for x in fewest_jumps_jumper.jump_types if '1' in x])

		that = '{} => {}, {}, {}'.format(number_jumps, level_3_boosts, level_2_boosts, level_1_boosts)
		print("fewest jumps: ", that)

		print()
		input("Below is a list of ALL stars visited (press ENTER): ")
		pretty_print(pristine_nodes, fewest_jumps_jumper)
		print()






















