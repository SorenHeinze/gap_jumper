#    "find_route" (v2.0)
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

# This file contains function in connection with the actual algorithm to find 
# a route. It exists mainly to keep other files a bit more tidy.

import additional_functions as af
from random import shuffle
from copy import deepcopy
import class_definitions as cd

# A jumper needs to be initialized in the startnode.
def create_jumper_at_start(start_star, all_nodes):
	starname = list(start_star.keys())[0]
	jumper = cd.Jumper(starname, 4)

	all_nodes[starname].jumper = jumper
	all_nodes[starname].visited = True



# The following function will never be triggered since all stars are considered
# as to be scoopbable by default (see comment in class Node to self.scoopable).
# However, it is the solution to an interesting problem and if the above 
# mentioned ever changes it may be of use.
# 
# Problem that may occur: No jumps take place because all possible jumps
# go to unscoopble stars, the jumper has just one jump left and within
# one regular jump distance no scoopable star is available. The latter 
# would have been checked already in node._check_free_stars().
# BUT, it may be possible that a scoopable star exists two (or more) jumps 
# away.
# All these possibilities could not be implemented in the regular code.
# Solution: Take the possibility of the latter into account by giving the 
# jumper fuel for one additional jump so that it can cross the gap to the 
# next (unscoopable) star and hope that after that a star exists that can be 
# used for refill.
def refuel_stuck_jumpers(all_nodes):
	for starname, node in all_nodes.items():
		jumper = node.jumper
		# This shall be done just for jumpers with an almost empty tank.
		# The main while loop in explore_path() has, at the point when this 
		# function is called, already checked for each jumper and all 
		# distances if it is possible to jump to a star and obviously failed 
		# to find one for all jumpers. 
		# If it is because of the case described above, giving these jumpers
		# fuel for another jump should solve this problem and when calling 
		# said main loop again it should find a star to jump to, if there is 
		# one.
		# < jumper >  should always exist, that is taken care of in 
		# explore_path(). However, just in case I check for it.
		if jumper and jumper.jumps_left == 1:
			jumper.jumps_left = 2
			jumper.magick_fuel_at.append(node.name)
			this = 'ATTENTION: needed magick re-fuel at {} to be '.format(node.name)
			that = 'able to jump. You need to get there with at least 2 jumps left! '
			siht = 'Otherwise you are stuck at the next star!'
			jumper.notes.append(this + that + siht)



# Just work with nodes that actually can send a jumper in the main while-loop
# in explore_path(). This function finds these nodes.
def get_nodes_that_can_send_jumpers(all_nodes, this_distance):
	starnames = []
	for starname, node in all_nodes.items():
		if node.jumper:
			# If neutron jumping is permitted, it shall always have priority
			# over all other jumps.
			if node.neutron:
				original_this_distance = deepcopy(this_distance)
				# Minus one because < this_distance > starts counting at zero.
				this_distance = len(node.reachable) - 1

			node._check_free_stars(this_distance)
			if len(node.can_jump_to) != 0:
				starnames.append(starname)

			# In case < this_distance > was changed due to a neutron 
			# boosted jump, it needs to be set back to the original 
			# value.
			if node.neutron:
				this_distance = deepcopy(original_this_distance)

	return starnames



# This does all the above and finds a way from start to end (or not).
def explore_path(all_nodes, final_node):
	# This is the index of the possible jump distances in the 
	# jump_distances-attribute of the Node-class.
	this_distance = 0
	# See below why I have this. And yes, I know that it is actually "magic".
	magick_fuel = False
	j = 0
	while not final_node.visited:
		j += 1
		starnames = get_nodes_that_can_send_jumpers(all_nodes, this_distance)

		# If no jump can take place with the given jump-distance ...
		if len(starnames) == 0:
			# ... allow for boosted jumps.
			this_distance += 1
			# A jumper can get stuck in a system JUST because it has just one
			# jump left in the tank and all reachable stars are unscoopable.
			# 
			# If this happens for all jumpers, give (once) a magick re-fuel. 
			# Do this just again, if a jump occured after the magick re-fuel. 
			# This is justified since EDSM does NOT have all stars. Thus it is 
			# likely that a real player could find a nearby scoopable star 
			# by just looking at the in-game galaxy map. Since I don't have 
			# this additional information I try to implement it with magick_fuel.
			# 
			# Due to many stars not having information about scoopability I had
			# to set the scoopable attribute of each node to True. Thus, I think
			# that this if-condition will never be triggered.
			# I keep it in case the above written ever changes.
			if this_distance == len(final_node.reachable) and not magick_fuel:
				magick_fuel = True
				this_distance = 0
				refuel_stuck_jumpers(all_nodes)

			elif this_distance == len(final_node.reachable):
				# If no way can be found even with the largest boost range, and
				# even after ONE magick fuel event took place, break the loop.
				break
		else:
			# I will run explore_path() to find the best way several time. 
			# However, it seems that once the program is called, that certain 
			# dict-related methods (e.g. .items()) return the items always in 
			# the same order during the momentary call if the program. 
			# Thus explore_path() will return always the same path. 
			# This is avoided by shuffling.
			shuffle(starnames)

			for starname in starnames:
				node = all_nodes[starname]
				# If neutron jumping is permitted, it shall always have 
				# priority over all other jumps. That means that 
				# < this_distance > is set to the maximum value in 
				# get_nodes_that_can_send_jumpers() and this needs to be 
				# taken care of here, too.
				if node.neutron:
					#print(this_distance)
					original_this_distance = deepcopy(this_distance)
					this_distance = len(node.reachable) - 1

				node._send_jumpers(this_distance)

				# In case < this_distance > was changed due to a neutron 
				# boosted jump, it needs to be set back to the original 
				# value.
				if node.neutron:
					this_distance = deepcopy(original_this_distance)

			# If any jump took place, try first to do a regular jump afterwards.
			this_distance = 0
			# If a jump is possible after a magick fuel event, everything can
			# be done as before. This includes that after the jump more magick 
			# fuel events can take place. Yes, in theory that means that a route 
			# may be just possible if magickally fuelled all the way.
			# I don't think that I have to worry about that. 
			magick_fuel = False



# This function figures out if the jumper that reached the final node during 
# the current loop uses less jumps or less boosts than the current best jumper.
# < data > is a tuple that contains information from the previous jumps
# < screen > is the instance of class ScreenWork() that calls this function.
def better_jumper(i, max_tries, jumper, data, screen):
	fewest_jumps_jumper = data[0]
	fewest_jumps = data[1]
	level_3_boosts = data[2]
	level_2_boosts = data[3]
	level_1_boosts = data[4]

	new_level_3_boosts = len([x for x in jumper.jump_types if '3' in x])
	new_level_2_boosts = len([x for x in jumper.jump_types if '2' in x])
	new_level_1_boosts = len([x for x in jumper.jump_types if '1' in x])
	number_jumps = len(jumper.visited_systems)

	text = screen.pathfinding_text.text().split('\nLast try')[0]
	this = 'Last try (#{} of {}) needed '.format(i + 1, max_tries)
	that = '{} jumps with {} level 3 boosts, '.format(number_jumps, \
																new_level_3_boosts)
	siht = '{} level 2 boosts, {} level 1 boosts'.format(new_level_2_boosts, \
																new_level_1_boosts)
	screen.pathfinding_text.setText(text + '\n' + this + that + siht)
	print(text + '\n' + this + that + siht)

	most_better = new_level_3_boosts < level_3_boosts
	
	medium_better = new_level_3_boosts <= level_3_boosts and \
										new_level_2_boosts < level_2_boosts

	least_better = new_level_3_boosts <= level_3_boosts and \
									new_level_2_boosts <= level_2_boosts and \
									new_level_1_boosts < level_1_boosts

	# ;)
	leastest_better = number_jumps < fewest_jumps and \
							new_level_3_boosts <= level_3_boosts and \
							new_level_2_boosts <= level_2_boosts and \
							new_level_1_boosts <= level_1_boosts


	if most_better or medium_better or least_better or leastest_better:
		fewest_jumps = number_jumps
		fewest_jumps_jumper = jumper

		level_1_boosts = new_level_1_boosts
		level_2_boosts = new_level_2_boosts
		level_3_boosts = new_level_3_boosts

	data = (fewest_jumps_jumper, fewest_jumps, level_3_boosts, \
										level_2_boosts, level_1_boosts)

	return data



# This is the main loop, that will search for the shortest and for the most 
# economic path as often as < max_tries >.
# < screen > is the instance of class ScreenWork() that calls this function.
def find_path(max_tries, stars, start_star, end_star, pristine_nodes, \
													neutron_boosting, screen):
	# This is just for the case that neutron boosting is allowed.
	way_back_jumper = None

	final_name = list(end_star.keys())[0]
	fewest_jumps_jumper = None
	fewest_jumps = 99999
	level_3_boosts = 99999
	level_2_boosts = 99999
	level_1_boosts = 99999

	# This is just to keep the list of parameters for better_jumper() short.
	data = (fewest_jumps_jumper, fewest_jumps, level_3_boosts, \
										level_2_boosts, level_2_boosts)

	i = 0
	while i < max_tries:
		if screen.mother.exiting.is_set():
			return

		this = screen.pathfinding_text.text().split('\n\n')[0]
		that = '\n\nTry #{} (of {}) to find a path ...'.format(i + 1, max_tries)
		# For subsequent iterations it shall be shown how many jumps the 
		# previous iteration needed. However, the first time around this would 
		# obviously fail.
		try:
			text = screen.pathfinding_text.text().split('find a path ...')[1]
		except IndexError:
			text = ''

		screen.pathfinding_text.setText(this + that + text)
		print(this + that + text)

		# After one loop all nodes are visited. Thus I need the "fresh", 
		# unvisited nodes for each loop.
		all_nodes = deepcopy(pristine_nodes)
		create_jumper_at_start(start_star, all_nodes)
		final_node = all_nodes[final_name]

		explore_path(all_nodes, final_node)

		if final_node.visited:
			jumper = final_node.jumper
		else:
			jumper = None

		if jumper and neutron_boosting and not way_back_jumper:
			# Since < all_nodes > is modified in explore_path I need to get the 
			# pristine nodes again.
			all_nodes = deepcopy(pristine_nodes)
			way_back_jumper = way_back(all_nodes, stars, start_star, end_star)

		if jumper:
			data = better_jumper(i, max_tries, jumper, data, screen)
		else:
			this = screen.pathfinding_text.text().split('\nLast try')[0]
			that = '\nLast try (#{} of {}) could NOT find a path.'.format(i + 1, max_tries)
			screen.pathfinding_text.setText(this + that)
			print(this + that + text)

		i += 1

	if jumper:
		this = "Finished finding a route. The results are shown below."
		screen.pathfinding_text.setText(this)

		screen.pathfinding_button.setText("Find path")

		fewest_jumps_jumper = data[0]

		screen.fewest_jumps_jumper = fewest_jumps_jumper
		screen.way_back_jumper = way_back_jumper
		# When all is done, send the signal to print the results.
		# See comment the extensive comment to < my_signal > the class ScreenWork
		# definition in screen_work.py why I have this here.
		screen.my_signal.emit('PRINT_ME')
	else:
		this = screen.pathfinding_text.text()
		that = '\nThe pathfnding algorithm failed to find a path.\nTry a ship '
		siht = 'with a larger jumprange.' 
		screen.pathfinding_text.setText(this + that + siht)

	screen.finding_path = False
	screen.pathfinding_button.setText("Find path")




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
		# away but within regular jump range exists.
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



# If neutron boosting is allowed a pilot can in principle get stuck. This is
# because she or he can use a neutron boosted jump to reach a non neutron 
# star containing system which is not within maximum jumponium boosted jump 
# range of any other system. This can mean that the goal will be reached but
# that maybe a way back is not possible. 
# Thus, if neutron boosting is allowed, this function is called once and it 
# checks once, if a way back is possible.
# It is basically the important path of find_path() again, just with start and
# goal switched and without trying finding a better path. One way back 
# is sufficient enough.
# < all_nodes > are all pristine nodes
# < start_star > and < end_star > are the _actual_ start and goal. The
# switching will take place inside this function.
def way_back(all_nodes, stars, start_star, end_star):
	final_name = list(start_star.keys())[0]
	create_jumper_at_start(end_star, all_nodes)
	final_node = all_nodes[final_name]

	explore_path(all_nodes, final_node)

	if final_node.visited:
		return final_node.jumper
	else:
		return None






















