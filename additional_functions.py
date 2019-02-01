#    "additional_functions" (v1.1)
#    Copyright 2019 Soren Heinze
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

# This file contains functions used in gap_jumper.py which did not fit into 
# any of the other files or the Node / Jumper-classes.

import class_definitions as cd
from math import sqrt


# This finds the closest system to a given point. Used e.g. to find the 
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



# This takes in all the star-data and creates node-objects.
def create_nodes(stars, jumpable_distances):
	all_nodes = {}

	for starname, data in stars.items():
		node = cd.Node(starname, data, jumpable_distances, stars, all_nodes)
		all_nodes[starname] = node

	return all_nodes



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



# To print the information about the path in a good way.
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






















