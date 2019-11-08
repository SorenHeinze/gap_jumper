#    "gap_jumper" (v1.1)
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

# This program is meant to be used to find a possible path in Elite Dangerous in 
# regions with extremely low star density. It takes the EDSM star-database and 
# finds a way from a given start- to a given end-point. If the spaceship can do 
# it at all, that is.
# 
# The route is NOT necessarily the shortest way, because highest priority was 
# set to save as much materials as possible by using boosted jumps just if no 
# other way can be found.
# 
# ATTENTION: Getting the initial information about available stars takes some time. 
# ATTENTION: You may imagine that it is probably not a good idea to run this
# program in regions with high (or even regular) star density. But who am I to 
# restrict your possibilities? 

import class_definitions as cd
import additional_functions as af
import find_systems_offline as off
import find_systems_online as on
import find_route as fr
import pickle
import logging
import requests

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ##   Input information below  ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##




# Beginning of program execution when run from the command line
if __name__ == "__main__":

	logs = logging.getLogger('gapjumper')
	logging.basicConfig()

	args = af.get_arguments()

	if args.verbose:
		logs.setLevel(logging.INFO)
		logs.info("Verbose logging enabled")

	if not args.range_on_fumes:
		args.range_on_fumes = args.jumprange + 0.01

	# ATTENTION: The very first value MUST be zero!
	# The last value is for neutron boosted jumps.
	jumpable_distances = [0] + [x*y for x in [1, 1.25, 1.5, 2.0] for y in [args.jumprange, args.range_on_fumes]] + [args.jumprange * 4]

	start_coords = dict(zip( ['x','y','z'], args.startcoords ))
	end_coords   = dict(zip( ['x','y','z'], args.destcoords ))

	max_tries = args.max_tries

	neutron_boosting = args.neutron_boosting

	# After the program was executed once, the database with all found stars 
	# for a given route and the corresponding notes are stored.
	# This is meant for the case that one and the same route shall be run
	# once more, without collecting all the data again, since the latter is
	# the bottle neck.
	# 
	# If the same stars shall be used but another ship with different
	# < jumpable_distances >.
	# 1.:  uncomment the first thing to load JUST the stars for this route. 
	# 2.: Below, comment out all in connection with af.find_systems().
	# 3.: Create the node informtion again with the new ship information by 
	# NOT having a comment around all in connection with af.create_nodes()
	# 4.: The rest of the program is the same.

	# Code path: load previously saved nodes
	if args.cached:
		filename = './stars'
		with open(filename, 'rb') as f:
			stars = pickle.load(f)

	# Code path: load stars from API or JSON
	else:
		if not args.starsfile:
			stars = on.find_systems_online(start_coords, end_coords)
		else:
			infile = args.starsfile
			stars = off.find_systems_offline(start_coords, end_coords, infile)

	if neutron_boosting:
		af.fetch_neutron_file()
		infile = './neutron-stars.csv'
		neutron_stars = off.collect_neutron_information(infile)
		off.update_stars_with_neutrons(stars, neutron_stars)

	# Yes, if cached stars are used this will be written to disk right after 
	# loading it. However, if neutron boosting is allowed, < stars > will have 
	# changed. Thus, it needs to be here.
	filename = './stars'
	with open(filename, 'wb') as f:
		pickle.dump(stars, f)

	# Always regenerate nodes, in case jump range changed
	# Still pickle nodes to disk, but only for debugging purposes.
	pristine_nodes = af.create_nodes(stars, jumpable_distances)

	filename = './all_nodes'
	with open(filename, 'wb') as f:
		pickle.dump(pristine_nodes, f)

	start_star, end_star = af.find_closest(stars, start_coords, end_coords)

	fewest_jumps_jumper, way_back_jumper = fr.find_path(max_tries, stars, \
						start_star, end_star, pristine_nodes, neutron_boosting)

	print()
	print("Start at: ", start_star)
	print("  End at: ", end_star)
	print("\nNumber of stars considered: ", len(stars))

	if neutron_boosting:
		this = "\n\nATTENTION: Neutron boosted jumps are enabled BUT you need "
		that = "to make sure for yourself that you DON'T RUN OUT OF FUEL!"
		print(this + that)

	af.print_jumper_information(pristine_nodes, fewest_jumps_jumper)

	if neutron_boosting:
		if not way_back_jumper:
			this = "\n\nATTENTION: Neutron jumping may allow you to get to your "
			that = "goal BUT no way back could be found.\nHowever, you may still "
			siht = "be able to find a way manually since not all systems are "
			taht = "registered in the database."
			print(this + that + siht + taht)
		else:
			print("\nYou will be able to get back. This is ONE possible way back.\n")
			af.print_jumper_information(pristine_nodes, way_back_jumper)






















