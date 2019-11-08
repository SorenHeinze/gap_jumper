#    "find_systems_offline" (v1.1)
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
# the offline-process.

from math import sqrt
import json
import additional_functions as af


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
# 250 (or even less) results in very many boosted jumps, which are to be 
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



# This is just to keep find_systems_offline() more tidy.
def get_star_into_dict(stars, start_coords, end_coords, \
											max_limits, min_limits, data):
	if within_limits(max_limits, min_limits, start_coords, end_coords, data):
		star_data = data['coords']
		star_data.update({'scoopable':True})
		star_data.update({'neutron':False})
		star_data.update({'id':data['id']})

		stars[data['name']] = star_data



# This is just to keep find_systems_offline() more tidy.
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
def find_systems_offline(start_coords, end_coords, infile):
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
			if i % 100000 == 0:
				print("checked star #{} ...".format(i))

	return stars



# The file that contains the information about all neutron stars has a 
# different structure than the systemsWithCoordinates.json file. Hence, it got
# its own function to find the necessary information in it.
def collect_neutron_information(infile):
	neutron = set()

	# Yes, the filename is hardcoded.
	with open('./neutron-stars.csv', 'r') as f:
		# The first line of the file is irrelevant.
		f.readline()
		for i, line in enumerate(f):
			id_number = int(line.split(',')[0].replace('"', ''))
			neutron.update([id_number])

	return neutron


# If neutron boosting shall be used, the stars that were figured out to be
# potential candidates need to be updated with the information if they are
# neutron stars. This function does that.
# < stars > is the dict with the information about said stars.
# < neutron_stars > is the set with the id's of the systems that contain 
# neutron stars.
def update_stars_with_neutrons(stars, neutron_stars):
	for starname, data in stars.items():
		if data['id'] in neutron_stars:
			stars[starname]['neutron'] = True















