#    "class_definitions" (v1.0)
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

# This file contains the class definitions of the Node- and Jumper-classes
# used in AA_gap_jumper.py 

from math import sqrt
from copy import deepcopy

# Nodes are beaically the stars, seen as bases that send out jumpers to
# reachable stars.
class Node(object):
	# < all_stars > is the dict that contains ALL stars-information, but it is 
	# NOT the dict that contains all nodes! Because in the beginning I have just
	# the information about the stars, but not yet the nodes.
	# < data > is a dict that contains the coordinates as 'x', 'y', 'z', if
	# it is scoopable and who discovered it.
	# ATTENTION: < jump_distances > must have 0 (zero) as the very first value 
	# and elements with even indice (e.g. element 3 => index 2) need to be 
	# jump length when running on fumes. _find_reachable_stars() depends on that!
	def __init__(self, name, data, jump_distances, all_stars, all_nodes):
		# This attribute is meant to be able to avoid jumps to non-scoopbable 
		# stars when already on fumes. However, in EDSM not all stars have this
		# information and I need to set self.scoopable to True to make the 
		# algorithm work at all. Thus, this feature is implemented in 
		# _check_free_stars() but is obviously rather useless.
		# However, if that ever changes, use < data['scoopable'] > as value 
		# to set this attribute.
		self.scoopable = data['scoopable']
		# I love pointers, because this will automatically fill up :).
		self.all_nodes = all_nodes
		self.visited = False
		self.can_jump_to = []
		self.jumper = None
		self.name = name
		self.data = data
		self.jump_distances = jump_distances
		# Each list is a list of the stars up to a certain distance.
		self.reachable = [[], [], [], [], [], [], [], []]

		self._find_reachable_stars(all_stars)


	# This calculates the distance to another star.
	def _this_distance(self, second_star_data):
		x_square = (self.data['x'] - second_star_data['x'])**2
		y_square = (self.data['y'] - second_star_data['y'])**2
		z_square = (self.data['z'] - second_star_data['z'])**2

		return sqrt(x_square + y_square + z_square)


	# This function finds all stars within the range(s) of the starship in use.
	# < jump_distances > is a list with all the possible jump distances and 
	# zero as the first element. See also comment to __init__().
	def _find_reachable_stars(self, all_stars):
		for name, data in all_stars.items():
			distance = self._this_distance(data)

			# ATTENTION: self.jump_distances contains zero as the first 
			# element to make this if-condition possible. Thus it is ONE 
			# element longer (!) than self.reachable and ...
			for i in range(len(self.jump_distances) - 1):
				# ... the element with index (i + 1) in self.jump_distances 
				# corresponds to ...
				if self.jump_distances[i] < distance and \
								distance < self.jump_distances[i + 1]:
					# ... element i in self.reachable.
					self.reachable[i].append(name)


	# < this_distance > is the index of the list in self.reachable
	def _check_free_stars(self, this_distance):
		self.can_jump_to = []
		self.emergence_scoop = None
		for name in self.reachable[this_distance]:
			next_star = self.all_nodes[name]
			if not next_star.visited:
				# Don't jump if your tank is empty afterwards and the star is 
				# unscoopable. But ...
				if self.jumper.jumps_left == 1 and not next_star.scoopable:
					# ... check if a star is nearby to re-fill the tank.
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
	def _send_jumpers(self, this_distance):
		# The .can_jump_to attribute is set when ._check_free_stars() is 
		# called in af.get_nodes_that_can_send_jumpers() which is calles
		# at the start of the while-loop in explore_path()
		for name in self.can_jump_to:
			new_jumper = deepcopy(self.jumper)
			new_jumper.visited_systems.append(name)
			new_jumper._add_jump_types(this_distance)

			next_star_data = self.all_nodes[name].data
			distance = self._this_distance(next_star_data)
			new_jumper.distances.append(distance)

			next_star = self.all_nodes[name]
			if next_star.scoopable:
				new_jumper.jumps_left = deepcopy(new_jumper.max_jumps)
			else:
				new_jumper.jumps_left -= 1

			next_star.jumper = new_jumper
			next_star.visited = True

		return True






# This is instantiated once and set at the starting node. If a node can send
# out jumpers, it deepcopies the jumper at this node and sets the new jumper
# to the nodes to be visited. This wil be the jump itself. Certain attributes 
# of the new jumper will be changed to accomodate for the fact that a jump
# took place.
class Jumper(object):
	def __init__(self, visited_systems, max_jumps):
		self.visited_systems = [visited_systems]
		self.max_jumps = max_jumps
		self.jumps_left = deepcopy(self.max_jumps)
		self.on_fumes = []
		self.scoop_stops = []
		self.notes = []
		self.magick_fuel_at = []
		self.on_fumes = []
		# This list will contain what kind of jump was done, e.g., "lvl 1 boost".
		self.jump_types = ['start']
		self.distances = [0]

	# I want the type of jump to be written in a certain way. Hence, this 
	# function.
	def _add_jump_types(self, this_distance):
		boost_type = int(this_distance/2)
		# The right hand expression evaluates to True or False, and yes, that 
		# can be done this way.
		# < + 1 > because this_distance starts counting at zero, and every
		# second distance type is on fumes.
		on_fumes = (this_distance + 1) % 2 == 0

		jump_types = 'B{}'.format(boost_type)

		if on_fumes:
			jump_types = jump_types + 'F'

		self.jump_types.append(jump_types)






















