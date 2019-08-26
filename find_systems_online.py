#    "find_systems_online" (v1.1)
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

# The processes for finding the systems of interest offline or online are quite 
# different. To keep a bit more order contains this file all the functions for 
# the online-process.

from math import sqrt
import json
import requests
import additional_functions as af
import logging
import time

logs = logging.getLogger('gapjumper.online')

# Things that are needed to find a point on the line between the start- and 
# the end-coords.
# This function does a lot but it seemed to make no sense to split it up.
def calculate_line_stuff(start_coords, end_coords):
	x_ = end_coords['x'] - start_coords['x']
	y_ = end_coords['y'] - start_coords['y']
	z_ = end_coords['z'] - start_coords['z']

	length = sqrt(x_**2 + y_**2 + z_**2)

	# < unit_vector > for the line from start- to end-coords.
	unit_vector = {}
	unit_vector['x'] = x_ / length
	unit_vector['y'] = y_ / length
	unit_vector['z'] = z_ / length

	# I want to look for stars approx. 500 ly around the line between start-
	# and end-coords. Thus I have to "extend" the line a bit.
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
	# comment to stars_in_cube() what that means).
	# I have just ONE vector, the unit_vector. Fortunately is the cross product 
	# between two vectors perpendicular to both. Thus I need just the second
	# vector. 
	# Fortunately (again), in 3D I just need to switch two "components"
	# add a minus to the second and set the third component to zero to get a 
	# vector perpendicular to the original vector. 
	# Example: vector = 3x + 4y + 5z, perpendicular = 4x - 3y + 0z
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



# The EDSM API can get me all stars in a cube with a side length of 200 ly.
# Testing has shown that I need cubes with a side length of ca. 1000 ly to get 
# good results in regions with a really low star density.
# Thus I build such cubes (well almost cubes) by stacking smaller cubes on each 
# other and get the stars in these smaller cubes. This is what happens here.
# Afterwards I move one cube length along the line and do the same. Stars
# that are "found again" will be removed. But the latter two things are 
# taking place in find_systems_online() and extract_information().
def stars_in_cubes_around_line(center_coords,
							   perpendicular_vector_1, perpendicular_vector_2):
	url = 'https://www.edsm.net/api-v1/cube-systems'
	# I want a stack of 5 x 5 cubes.
	counter_1 = -2
	counter_2 = -2

	all_stars = []
	while counter_1 < 3:
		while counter_2 < 3:
			# Just some vector addition.
			x_ = center_coords['x'] + 200 * counter_1 * perpendicular_vector_1['x'] + \
												200 * counter_2 * perpendicular_vector_2['x']
			y_ = center_coords['y'] + 200 * counter_1 * perpendicular_vector_1['y'] + \
												200 * counter_2 * perpendicular_vector_2['y']
			z_ = center_coords['z'] + 200 * counter_1 * perpendicular_vector_1['z'] + \
												200 * counter_2 * perpendicular_vector_2['z']

			payload = {'x':x_, 'y':y_, 'z':z_, 'size':200, 'showCoordinates':1, 'showPrimaryStar':1}
			logs.info(url, payload)
			systems = requests.get(url, params = payload)
			if systems.status_code != requests.codes.ok:
				logs.error("HTTP ERROR ", systems.status_code, url, payload)
				break
			all_stars.append(systems.json())

			## Quick and dirty rate-limiting
			if systems.headers['x-rate-limit-remaining'] == 0 and systems.headers['x-rate-limit-reset'] > 0:
				logs.warning("Rate limit hit, sleeping for %d seconds", systems.headers['x-rate-limit-reset'])
				time.sleep(systems.headers['x-rate-limit-reset'])

			counter_2 += 1

		counter_1 += 1
		counter_2 = -2

	return all_stars


# The get() in stars_in_cubes_around_line() will just return information about
# the main star of a system. However, it may be the case that the main star of 
# a system is not scoopbable, but other stars in the same system are.
# In this case this function is called in extract_information() to figure
# exactly that out.
def system_has_scoopable_star(starname):
	url = 'https://www.edsm.net/api-system-v1/bodies'
	payload = {'systemName':starname}

	# < data > is a dict that has a key 'bodies' which contains as elements 
	# dicts with the information about all celestial bodies in that system.
	data = requests.get(url, params = payload).json()

	for body in data['bodies']:
		# Not all bodies have the attribute < isScoopable >.
		try:
			if body['isScoopable']:
				# It is enough to find ONE star that is scoopable.
				return True
		except KeyError:
			pass

		return False



# Of all the information returned by stars_in_cubes_around_line() I need JUST 
# the things processed in this function.
# < stars > is a dict which contains each systems information between start- 
# and end-coords in the given corridor of stacked cubes as returned by 
# stars_in_cubes_around_line().
def extract_information(stars, this_section_stars):
	for element in this_section_stars:
		# An element in < this_section_stars > can be a list with one or
		# more dicts or an empty dict.
		if len(element) > 0:
			for this_dict in element:
				starname = this_dict['name']
				coords = this_dict['coords']
				# This can be True or False or None.
				scoopable = this_dict['primaryStar']['isScoopable']

				if not scoopable and system_has_scoopable_star(starname):
					scoopable = True

				stars[starname] = {}
				stars[starname].update(coords)
				stars[starname]['scoopable'] = scoopable

	return stars



# This does all of the above.
# < start_coords > and < end_coords > are dicts with the (approximate) 
# coordinates of the star at the start and the star at the end.
def find_systems_online(start_coords, end_coords):
	# < unit_vector > is for the line from start- to end-coords.
	unit_vector, perpendicular_vector_1, perpendicular_vector_2, \
		start_of_line, end_of_line = calculate_line_stuff(start_coords, end_coords)

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
		difference = af.distance_to_point(center_coords, end_of_line)

		this = "Getting all systems between start and end "
		that = "(distance = {} ly). This will take some time...".format(int(difference))
		print(this + that)

		this_section_stars = stars_in_cubes_around_line(center_coords, \
										perpendicular_vector_1, perpendicular_vector_2)
		stars = extract_information(stars, this_section_stars)

		# In general is the line NOT perpendicular to the cubes sides. 
		# Hence, the following will lead to the overlap of some cubes. 
		# Something I can live with, since missing stars due to non-overlap
		# would be more seriuos.
		center_coords['x'] = center_coords['x'] + 200 * unit_vector['x']
		center_coords['y'] = center_coords['y'] + 200 * unit_vector['y']
		center_coords['z'] = center_coords['z'] + 200 * unit_vector['z']

	return stars






















