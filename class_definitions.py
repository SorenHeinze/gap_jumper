#    "class_definitions" (v2.0)
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

# This file contains the class definitions of the Node- and Jumper-classes
# used in gap_jumper.py 

from math import sqrt
from copy import deepcopy

# Nodes are beaically the stars, seen as bases that send out jumpers to
# reachable stars.
class Node(object):
	# < all_stars > is the dict that contains ALL stars-information, but it is 
	# NOT the dict that contains all nodes! Because in the beginning I have just
	# the information about the stars, but not yet the nodes.
	# < data > is a dict that contains the coordinates as 'x', 'y', 'z' and if
	# a star is scoopable.
	# ATTENTION: < jump_distances > must have 0 (zero) as the very first value 
	# and elements with even indice (e.g. element 3 => index 2) need to be 
	# jump length when running on fumes. _find_reachable_stars() depends on that!
	def __init__(self, name, data, jump_distances, all_stars, all_nodes):
		self.name = name
		# This attribute is meant to be able to avoid jumps to non-scoopbable 
		# stars when already on fumes. However, in EDSM not all stars have this
		# information and I need to set self.scoopable to True to make the 
		# algorithm work at all. Thus, this feature is implemented in 
		# _check_free_stars() but is obviously rather useless.
		# However, if that ever changes, use < data['scoopable'] > as value 
		# to set this attribute.
		self.scoopable = True
		# I love pointers, because this will automatically fill up :).
		self.all_nodes = all_nodes
		# The algorithm works by sending "jumpers" from one star to the next.
		# If one star can be reached from another is defined by < jump_distances >
		self.jump_distances = jump_distances
		# The jumper mentioned above. It will become later a class Jumper object.
		self.jumper = None
		# If a system was visited by a jumper it shall not be visited again.
		# Actually this attribute is redundant, since if a system contains a 
		# jumper it is automatically visited. So the latter could be used instead.
		# However, I figured that out when everything was finished and thus
		# kept < visited > to not break anything.
		self.visited = False
		# This will be filled when _check_free_stars() is called. It will contain
		# the names of the systems which have not yet been visited and which are
		# within a give jump range.
		self.can_jump_to = []
		# I want to keep the original dict for this star, just in case.
		# It also contains the x, y and z coordinates of the system.
		self.data = data
		# Neutron stars will allow extremely long jumps, but just neutron
		# stars allow that. Hence, I'd like have easy access to this attribute
		# of a star
		self.neutron = self.data['neutron']
		# See comment to _calculate_limits() what I'm doing here and why.
		self._calculate_limits()
		# I figure once out which other stars can be reached with a given jump
		# range from the given system. So each list is a list of the stars up 
		# to a certain distance.
		# self.jump_distances has zero as the very first element and is thus
		# one element longer than self.reachable shall be.
		self.reachable = [[] for i in range(len(self.jump_distances) - 1)]
		# And finally figure out all the stars that can be reached with a
		# given jumprange.
		self._find_reachable_stars(all_stars)


	# Creating these nodes takes A LOT of time if many nodes are to be created.
	# It seems that calculating the distances to all other stars requires most 
	# of this time. Hence, I decided that the distances shall just be 
	# calculated if a star actually can be reached. The latter means that it
	# is "in a box", with side length's equal to the maximum jump range, 
	# around this node. 
	# This decreased the time to create all the nodes by a factor of twenty (!).
	# This function creates the boundaries of said box.
	def _calculate_limits(self):
		if self.neutron:
			half_cube_length = self.jump_distances[-1]
		else:
			half_cube_length = self.jump_distances[-2]

		self.x_upper = self.data['x'] + half_cube_length
		self.x_lower = self.data['x'] - half_cube_length
		self.y_upper = self.data['y'] + half_cube_length
		self.y_lower = self.data['y'] - half_cube_length
		self.z_upper = self.data['z'] + half_cube_length
		self.z_lower = self.data['z'] - half_cube_length


	# This calculates the distance to another star.
	# This is basically the same what is done in additional_functions.py => 
	# distance_to_point(). However, I wanted this also to be a method of this 
	# class.
	def _this_distance(self, second_star_data):
		x_square = (self.data['x'] - second_star_data['x'])**2
		y_square = (self.data['y'] - second_star_data['y'])**2
		z_square = (self.data['z'] - second_star_data['z'])**2

		return sqrt(x_square + y_square + z_square)


	# This function checks for if a star is within the box of reachable stars
	# around a given node. See also comment to _calculate_limits().
	def _in_box(self, second_star_data):
		first = self.x_lower < second_star_data['x'] < self.x_upper
		second = self.y_lower < second_star_data['y'] < self.y_upper
		third = self.z_lower < second_star_data['z'] < self.z_upper

		if first and second and third:
			return True
		else:
			return False


	# This function finds all stars within the range(s) of the starship in use.
	# < jump_distances > is a list with all the possible jump distances and 
	# zero as the first element. See also comment to __init__().
	def _find_reachable_stars(self, all_stars):
		for name, data in all_stars.items():
			# Don't do all the calculations if the star couldn't be 
			# reached anyway.
			# ATTENTION: Since the sphere around this node is smaller than the 
			# square box the below calculations still need to take care of 
			# case that a star is in the box but outside maximum jumping 
			# distance. This is implemented below.
			if not self._in_box(data):
				continue

			distance = self._this_distance(data)

			# The cube contains volumes outside the sphere of the maximum
			# jump range around a node. Don't do anything if another star falls
			# into such an area.
			# Remember that the last element in self.jump_distances is the 
			# jump distance for neutron boosted jumps.
			if not self.neutron and distance > self.jump_distances[-2]:
				continue
			elif distance > self.jump_distances[-1]:
				continue

			# ATTENTION: self.jump_distances contains zero as the first 
			# element to make this if-condition possible. Thus it is ONE 
			# element longer (!) than self.reachable and ...
			for i in range(len(self.jump_distances) - 1):
				# ... the element with index (i + 1) in self.jump_distances 
				# corresponds to ...
				if self.jump_distances[i] <= distance and \
								distance < self.jump_distances[i + 1]:
					# ... element i in self.reachable.
					self.reachable[i].append(name)


	# This method checks if the nearby stystems are free to jump to.
	# < this_distance > is the index of the list in self.reachable. Do NOT 
	# confuse with the method _this_distance()!
	def _check_free_stars(self, this_distance):
		self.can_jump_to = []
		for name in self.reachable[this_distance]:
			next_star = self.all_nodes[name]
			if not next_star.visited:
				# The following will never be triggered as of now, since the 
				# .scoopable attribute is set be default to True. However, this 
				# if-condition is meant to NOT allow a jump if the tank is empty 
				# afterwards and the next star is unscoopable. 
				# If this information ever will be available for all systems in 
				# the EDSM database, it is automatically available (see also 
				# comment above to self.scoopable).
				if self.jumper.jumps_left == 1 and not next_star.scoopable:
					# Check if a star is nearby to re-fill the tank.
					if self._refill_at_nearest_scoopable(name):
						self.jumper.jumps_left = self.jumper.max_jumps - 1
						self.can_jump_to.append(name)
					else:
						pass
				# If (this_distance  + 1) is even it is a jump distance for jumping 
				# on fumes. In this case the next star needs to be scoopable
				# because otherwise the jumper would strand there!
				elif (this_distance + 1) % 2 == 0 and next_star.scoopable:
					self.jumper.jumps_left = 1
					self.jumper.on_fumes.append((self.name, next_star.name))
					this = 'On fumes jump from {} to {}'.format(self.name, next_star.name)
					self.jumper.notes.append(this)
					self.can_jump_to.append(name)
				else:
					self.can_jump_to.append(name)


	# Case not covered in _check_free_stars(): Jumper won't jump because the
	# tank is almost empty and the next star is not scoopable but another 
	# nearby star could be used to re-fill but was already visited.
	# Solution: Make a detour to the scoopable star, re-fill, fly back and make 
	# the jump. However, this shall be done JUST for regular jumps and the 
	# minimum number of jumps with full tank must be three.
	# ATTENTION: Just stars in regular jump distance will be considered for 
	# refill!
	# For the time being, the if-condition in _check_free_stars() which calls
	# this function will never be triggered, will this function also never be
	# used (see also comment in _check_free_stars()).
	def _refill_at_nearest_scoopable(self, point_of_origin):
		for name in self.reachable[0]:
			next_star = self.all_nodes[name]
			if next_star.scoopable:
				this = (point_of_origin, name, point_of_origin)
				self.jumper.scoop_stops.append(this)
				this = 'Refill needed at {}! '.format(point_of_origin)
				that = 'Jump to {} and back to {}.'.format(name, point_of_origin)
				self.jumper.notes.append(this + that)

				return True

		# If no scoopable star is near, the jumper is stuck.
		return False


	# This is basically the method called on each node-instance if the 
	# node houses a jumper.
	# this is the heart of the algorithm to explore the network of stars to 
	# find a route.
	def _send_jumpers(self, this_distance):
		# The .can_jump_to attribute is set when ._check_free_stars() is 
		# called in additional_functions.py => get_nodes_that_can_send_jumpers() 
		# which is called at the start of the while-loop in explore_path() in
		# additional_functions.py.
		for name in self.can_jump_to:
			new_jumper = deepcopy(self.jumper)
			new_jumper.visited_systems.append(name)
			new_jumper._add_jump_types(this_distance)

			next_star = self.all_nodes[name]
			next_star_data = next_star.data
			distance = self._this_distance(next_star_data)
			new_jumper.distances.append(distance)

			# Another condition that is of little use as long the information
			# about scoopability is not available for all systems in EDSM.
			if next_star.scoopable:
				new_jumper.jumps_left = deepcopy(new_jumper.max_jumps)
			else:
				new_jumper.jumps_left -= 1

			next_star.jumper = new_jumper
			next_star.visited = True

		return True






# This is instantiated once and set at the starting node. If a node can send
# out jumpers, it deepcopies its jumper and sets the new jumper to the nodes to 
# be visited. This wil be the jump itself. Certain attributes of the new jumper 
# will be changed to accomodate for the fact that a jump took place.
class Jumper(object):
	def __init__(self, visited_systems, max_jumps):
		# The list with all the systems visited by this jumper. This is what
		# all the shebang is for.
		self.visited_systems = [visited_systems]
		# Number of jumps without re-fueling.
		self.max_jumps = max_jumps
		# This is the number of jumps "left in the tank" after a jump took place.
		self.jumps_left = deepcopy(self.max_jumps)
		# Additional information. Was interesting during testing, but will 
		# not be delivered to the user (but it is easily available).
		self.on_fumes = []
		# Dito.
		self.scoop_stops = []
		# Dito.
		self.notes = []
		# Dito. See comment in additional_functions.py => explore_path() what
		# this is about. And yes, i know that magick is written wrong.
		self.magick_fuel_at = []
		# Dito.
		self.on_fumes = []
		# This list will contain what kind of jump was done, e.g., 'B1F' for a
		# "grade 1 boosted jump on fumes". THIS information will be delivered 
		# to the user.
		self.jump_types = ['start']
		# The distanced between the systems visited. This information will also 
		# be delivered to the user.
		self.distances = [0]


	# I want the type of jump to be written in a certain way. Hence, this 
	# function.
	def _add_jump_types(self, this_distance):
		boost_type = int(this_distance/2)
		# The right hand expression evaluates to True or False, and yes, that 
		# can be done this way.
		# < + 1 > because this_distance starts counting at zero, and every
		# second distance type is on fumes (every number in 
		# class Node => .jump_distances with an even index).
		on_fumes = (this_distance + 1) % 2 == 0
		neutron_boosted = (this_distance + 1) % 9 == 0

		jump_types = 'B{}'.format(boost_type)

		if on_fumes:
			jump_types = jump_types + 'F'
		elif neutron_boosted:
			jump_types = 'neutron'

		self.jump_types.append(jump_types)






















