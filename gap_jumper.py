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
import argparse
import logging

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ##   Input information below  ## ## ## ## ##
## ## ## ## ##                            ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

# The path where the systemsWithCoordinates.json can be found. In this folder 
# the found systems file will be stored, too.
path = '/home/soren/Desktop/gap_jumper_collaboration/gap_jumper/data_2/'

# In case neutron boosting shall be allowed, the necessary information must
# be provided. The file with all known neutron stars can be found here: 
# https://edastro.com/mapcharts/files/neutron-stars.csv
# ATTENTION: It is assumed that this file will be in the same folder as the
# < coordinates_file >.
neutron_file = 'neutron-stars.csv'

## Beginning of program execution when run from the command line
if __name__ == "__main__":

	logs = logging.getLogger('gapjumper')
	logging.basicConfig()
	parser = argparse.ArgumentParser(
		description="""You want to directly cross from one spiral arm of the
		galaxy to another but there is this giant gap between them?
		This program helps you to find a way.

		Default behavior is to use the EDSM API to load stars on-demand. Use
		the --starsfile option if you have downloaded the systemsWithCoordinates.json
		nigthly dump from EDSM.""",
		epilog="See README.md for further information.")

	# From the parser-documentation:
	# Any internal < - > characters will be converted to < _ > characters to 
	# make sure the string is a valid attribute name.
	parser.add_argument('--range','-r', metavar='LY', required=True, type=float, 
						help="Ship range with a full fuel tank (required)")
	parser.add_argument('--range-on-fumes','-rf', metavar='LY', type=float,
						help="Ship range with fuel for one jump (defaults equal to range)")
	parser.add_argument('--startcoords','-s', nargs=3, metavar=('X','Y','Z'), type=float, required=True,
						help="Galactic coordinates to start routing from")
	parser.add_argument('--destcoords','-d', nargs=3, metavar=('X','Y','Z'), type=float, required=True,
						help="Galactic coordinates of target destination")
	parser.add_argument('--neutron-boosting','-nb', metavar=('True/False'), type=bool, default=False,
						help="Utilize Neutron boosting. If set to True the file must be in the folder as specified in the sourcecode (for now)")
	parser.add_argument('--cached', action='store_true', help="Reuse nodes data from previous run")
	parser.add_argument('--starsfile', metavar='FILE',
						help="Path to EDSM system coordinates JSON file")
	parser.add_argument('--max-tries','-N', metavar='N', type=int, default=23,
						help="How many times to shuffle and reroute before returning best result (default 23)")
	parser.add_argument('--verbose','-v', action='store_true', help='Enable verbose logging')
	args = parser.parse_args()

	if args.verbose:
		logs.setLevel(logging.INFO)
		logs.info("Verbose logging enabled")

	if not args.range_on_fumes:
		args.range_on_fumes = args.range+0.01

	# ATTENTION: The very first value MUST be zero!
	jumpable_distances = [0] + [x*y for x in [1, 1.25, 1.5, 2.0] for y in [args.range, args.range_on_fumes]] + [args.range * 4]

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

## Code path: load previously saved nodes
	if args.cached:
		filename = path + 'stars_on'
		with open(filename, 'rb') as f:
			stars = pickle.load(f)

## Code path: load stars from API or JSON
	else:
		if not args.starsfile:
			stars = on.find_systems_online(start_coords, end_coords)
		else:
			infile = args.starsfile
			stars = off.find_systems_offline(start_coords, end_coords, infile)

	if neutron_boosting:
		infile = path + neutron_file
		neutron_stars = off.collect_neutron_information(infile)
		off.update_stars_with_neutrons(stars, neutron_stars)

	# Yes, if cached stars are used this will be written to disk right after 
	# loading it. However, if neutron boosting is allowed, < stars > will have 
	# changed. Thus, it needs to be here.
	filename = path + 'stars_on'
	with open(filename, 'wb') as f:
		pickle.dump(stars, f)


## Always regenerate nodes, in case jump range changed
## Still pickle nodes to disk, but only for debugging purposes
	pristine_nodes = af.create_nodes(stars, jumpable_distances)

	filename = path + 'all_nodes'
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
















