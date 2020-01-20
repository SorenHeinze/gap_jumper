#    "screen_work" (v2.0)
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

# This file contains the class definition of the "work layer" of the main (and 
# only) window of the gui in which all the actual work is performed ... not in 
# the screen/gui of course, but in the background, but all the buttons pressed 
# here lead to the necessary actions being performed.

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QSpacerItem, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal
import threading
from time import sleep
import os
import find_systems_offline as off
import find_systems_online as on
import pickle
import additional_functions as af
import find_route as fr


# The class definition of the the "work layer" of the main window.
class ScreenWork(QWidget):
	# Whoa! This is complicated.
	# 
	# Original problem: I wanted the textfield < self.results >, 
	# a QPlainTextEdit() instance, instantiated in self._make_pathfinding_stuff(), 
	# to display the results once the algorithm is finished.
	# 
	# First, as for everything else, I started a separate thread that just looked
	# if the pathfinding algorithm was still running and if not it would have 
	# printed the results. That did not work. I've got an error stating that 
	# the text in the textfield could not be set since the textfield belonged
	# to a different thread/parent.
	# 
	# Second, I've tried to set the text in the textfield directly from the 
	# pathfinding function after it finished. I do this for other attributes,
	# like e.g., some QLabel() instances. Strangely, that gave the same error.
	# 
	# Third, I've decorated the an attribute of this class. This attribute is
	# set by the pathfinding algorithm once it is finished, thus indicating,
	# that the results can be printed in the textfield. The idea was than that 
	# decorating said attribute with a getter and setter could set the text in
	# said textfield. But once again I've got the same error.
	# 
	# Fourth, signal -> slot ... and this is where it gets complicated.
	# 
	# ATTENTION: a signal needs to be an attribute of the class. HOWEVER (!), 
	# it CAN NOT be set with < self.my_signal > in __init__(). That won't work.
	# Thus, a signal needs to be declared as an attribute of the class even 
	# before __init__().
	# 
	# A signal has as a variable what kind of signal it shall emit. In this 
	# case here that doesn't really matter but I've set it to be a string.
	# 
	# Below in the __init__() I connect < my_signal > to the function that 
	# shall be called when the said signal is emitted. 
	# And this function finally sets the text in the textfield!
	# 
	# I've pieced this together by reading many things on the internet. The
	# examples there were strange and could not really be used.
	# Now that I understand this a bit more, this seems to be the best source:
	# https://www.riverbankcomputing.com/static/Docs/PyQt5/signals_slots.html
	my_signal = pyqtSignal(str)

	# < mother > is the main window instance that actually instantiates this 
	# class.
	def __init__(self, mother, x_position, y_position):
		super(ScreenWork, self).__init__()

		self.my_signal.connect(self._print_results)

		self.mother = mother
		# Some attributes that are set to True by specific methods or outside 
		# functions when certain tasks are carried out and set back to False, 
		# once these tasks are done. In connection with separate threads is 
		# this the way how I check if a certain taks was finished so that 
		# the next task can start. An example would be downloading and saving
		# of the neutron-stars file.
		self.downloading_neutron_file = False
		self.searching_stars = False
		self.creating_nodes = False
		self.preparing_neutron_stars = False
		self.finding_path = False
		self.loading_files = False
		# These are the "containers" (al of them dicts) that carry specific 
		# information needed for the the pathfinding algorithm. 
		self.stars = None
		self.neutron_stars = None
		self.pristine_nodes = None
		self.start_star = None
		self.end_star = None
		# The final results.
		self.fewest_jumps_jumper = None
		self.way_back_jumper = None

		self._initUI(x_position, y_position)


	# For correct closing of all threads after the gui is closed I had to 
	# expand the gui closing procedure. See the comment to closeEvent() 
	# of class Motherwindow why / how I do this.
	# Instead of writing everything again I just call the modified method.
	def closeEvent(self, event):
		self.mother.closeEvent(event)


	# This method instantiates all the elements that shall be shown on screen.
	# Well, actually it mostly calls further methods that do the actual work. 
	# It exists mainly to keep __init__() more tidy.
	def _initUI(self, x_position, y_position):
		self.setGeometry(x_position, y_position, 1000, 500)
		self.layout = QGridLayout()
		self.setLayout(self.layout)

		spacer = QSpacerItem(23, 23)

		# First, the back button.
		self.back_button = QPushButton('Back')
		self.back_button.clicked.connect(self.back_button_action)
		self.layout.addWidget(self.back_button, 1, 0)

		# Second, the stuff for getting the neutron stars-file.
		# This will be hidden by default or if the file was recently downloaded.
		self._make_neutron_file_stuff()

		# Third, the stuff for finding the relevant stars in the 
		# systemsWithCoordinates file.
		# Will be hidden if the "use cached stars" option is used.
		self._make_star_search_stuff()

		# Fourth, the stuff for creating the nodes, once the relevant stars 
		# have been found.
		self._make_create_nodes_stuff()

		# Fifth, the stuff for finding the path
		self._make_pathfinding_stuff()

		# Some spacers for better looks, ...
		self.layout.addItem(spacer, 2, 0)
		self.layout.addItem(spacer, 5, 0)
		self.layout.addItem(spacer, 8, 0)
		self.layout.addItem(spacer, 11, 0)
		self.layout.addItem(spacer, 14, 0)
		self.layout.addItem(spacer, 16, 0)


	# The things that shall be done when the back button is pressed.
	# Most of the things stated here were discovered during testing and to 
	# not clutter up other functions this method was written.
	def back_button_action(self):
		# This is obvious, isn't it.
		self.mother.stacked_layout.setCurrentIndex(0)

		# The button to download the neutron-stars file is hidden by default.
		# If one run is started WITH neutron boosting this button will be shown.
		# Thus, when pressing the back button, this needs to be hidden again.
		if not self.downloading_neutron_file:
			self.neutron_text.hide()
			self.download_neutron_file_button.hide()

		# The program could do the search once with neutron boosts activated 
		# and this parameter is set to True because everything is OK with the 
		# neutron-stars file. But then the back button is pressed and the user 
		# decides to delete said file. Thus, the conditions for this parameter 
		# need to be checked again.
		self.mother.neutron_file_ok = False

		# If a user uses the cached file for one run the respective button will 
		# be hidden. Pressing back and trying another run while NOT using the 
		# cached file needs than to show the button again. 
		if not self.searching_stars:
			this = "Press the button below to start the search for relevant stars. "
			that = "This will take a while!"
			self.mother.screen_work.star_search_text.setText(this + that)
			self.mother.screen_work.star_search_button.show()

		# This is because of some weird situation in which once the user states 
		# the systemsWithCoordinates-file, presses back and then doesn't. From
		# the previous run < self.mother.starsfile > would still be set if I 
		# wouldn't reset this attribute.
		self.mother.starsfile = None


	# Here follow all the methods that actually create the stuff to be shown
	# on screen.

	# This method exists just to keep _initUI() a bit more tidy.
	def _make_neutron_file_stuff(self):
		# The text is set when the continue button of the previous screen is 
		# pressed.
		self.neutron_text = QLabel()
		self.layout.addWidget(self.neutron_text, 3, 0)

		self.download_neutron_file_button = QPushButton('Download neutron-stars.csv')
		self.download_neutron_file_button.clicked.connect(self._download_neutron_file)
		self.layout.addWidget(self.download_neutron_file_button, 4, 0)

		if not self.mother.neutron_boosting:
			self.neutron_text.hide()
			self.download_neutron_file_button.hide()


	# Dito
	def _make_star_search_stuff(self):
		# Dito
		self.star_search_text = QLabel()
		self.layout.addWidget(self.star_search_text, 6, 0)

		self.star_search_button = QPushButton("Search for relevant stars")
		self.star_search_button.clicked.connect(self._search_stars)
		self.layout.addWidget(self.star_search_button, 7, 0)


	# Dito
	def _make_create_nodes_stuff(self):
		
		self.create_nodes_text = QLabel()
		self.layout.addWidget(self.create_nodes_text, 9, 0)

		self.create_nodes_button = QPushButton("Prepare information for pathfinding")
		self.create_nodes_button.clicked.connect(self._create_the_nodes)
		self.layout.addWidget(self.create_nodes_button, 10, 0)


	# Dito
	def _make_pathfinding_stuff(self):
		# Dito
		self.pathfinding_text = QLabel()
		self.layout.addWidget(self.pathfinding_text, 12, 0)

		self.pathfinding_button = QPushButton("Find path")
		self.pathfinding_button.clicked.connect(self._find_path)
		self.layout.addWidget(self.pathfinding_button, 13, 0)

		self.results = QPlainTextEdit()
		self.layout.addWidget(self.results, 15, 0)


	# Here follow the definitions of the methods to be called when a button is 
	# pressed. This includes also subsequent methods that are called by the
	# former.

	# This method checks how far the download of the neutron-stars file has 
	# come. It's target of a separate thread in _download_neutron_file().
	# I unfortunately can NOT check how far the download progress has come
	# since (as of 2020-01-16) no content length header available for this file.
	def _check_download_progress(self):
		i = 0
		# self.downloading_neutron_file is set in on.fetch_neutron_file().
		while self.downloading_neutron_file:
			this = "Still Downloading the Neutron Stars file ({} s) ...".format(i)
			self.neutron_text.setText(this)

			i += 1
			sleep(1)

		self.neutron_text.setText("Finished downloading the Neutron Stars file.")

		self.mother.neutron_file_ok = True


	# The actions carried out when the < self.download_neutron_file_button >
	# is pressed.
	def _download_neutron_file(self):
		self.download_neutron_file_button.hide()

		download_thread = threading.Thread(target = on.fetch_neutron_file, \
																args = [self])
		progress_thread = threading.Thread(target = self._check_download_progress, \
																args = [])
		download_thread.start()
		progress_thread.start()


	# The target of the < save_thread > in _search_stars().
	# < running > is the name of the respective attribute of this class that 
	# monitors if the relevant search process is ... well, still running.
	# < save_this > is the name of the attribute of this class that contains 
	# the information that shall be saved. The respective attributes are 
	# set in the respective functions and one example would be < self.stars >.
	# < textfield > is the respective textfield.
	# < outfile > is the relevant outfile.
	def _save_information(self, running, save_this, textfield, outfile):
		# Don't do anything as long is the search isn't finished.
		while getattr(self, running):
			# For correct closing of all threads after the gui is closed the 
			# gui close event sets an attribute of the class Motherwindow
			# instance. This function checks if said attribute is set and 
			# and returns if it is, which will close the thread that called 
			# this function gracefully.
			if self.mother.exiting.is_set():
				return

			sleep(1)

		save_that = getattr(self, save_this)

		this = textfield.text() + '\n\n'
		that = 'Saving ...'
		textfield.setText(this + that)

		# ATTENTION: IF the gui is closed during saving, DON'T interrupt the 
		# thread! This could lead to ressources not being freed properly.
		with open(outfile, 'wb') as f:
			pickle.dump(save_that, f)

		this = textfield.text().split('Saving ...')[0]
		that = 'Finished saving. The next step will now use this information '
		siht = 'and can be started.'
		textfield.setText(this + that + siht)


	# The actions carried out when the < self.star_search_button > is pressed.
	def _search_stars(self):
		# This is just to keep the second and third if-condition below shorter.
		first = self.mother.offline_mode
		second = self.mother.starsfile
		third = os.path.isfile('./systemsWithCoordinates.json')
		# It is possible that < self.mother.starsfile > is None. That would 
		# lead to errors.
		try:
			fourth = os.path.isfile(self.mother.starsfile)
		except TypeError:
			fourth = False

		# Don't do anything if one search process has already started. This 
		# would start another thread and BOTH threads would search for stars.
		# < self.searching_stars > is set in the respective search function.
		if self.searching_stars:
			this = "ATTENTION: A search is ongoing. Try again when finished."
			self.star_search_text.setText(this)
			return
		# This should never be triggered since the continue action of the 
		# user input screen already checks this ... BUT, this is relevant if 
		# the user deletesthe file after passing the previous mentioned check.
		elif first and second and not fourth:
			this = "ATTENTION: The stated systemsWithCoordinates-file could "
			that = "not be found."
			self.star_search_text.setText(this + that)
			return
		# More or less dito.
		elif first and not second and not third:
			this = 'ATTENTION: Could not find the systemsWithCoordinates.json'
			that = '-file. Please download it and copy it into the '
			siht = 'installation directory. Or provide the path to said file.'
			self.star_search_text.setText(this + that + siht)
			return

		self.star_search_text.setText("Searching ...")

		start_coords = self.mother.start_coords
		end_coords = self.mother.end_coords

		# Here the actual search is started. The search function sets
		# < self.searching_stars > to True when it starts and to False when it
		# finishes.
		if self.mother.offline_mode:
			infile = self.mother.starsfile

			# off.find_systems_offline() needs several parameters. Listing them
			# all for the lambda statement is ... well, impractical. This 
			# however can be solved with the < * > operator that "unpacks" 
			# the < variables > list into its single elements.
			# See second method here: https://www.geeksforgeeks.org/ ...
			# ... python-split-and-pass-list-as-separate-parameter/
			# 
			# off.find_systems_offline puts the dictionary with the relevant 
			# stars directly into < self.stars > of this class.
			t = lambda variables: off.find_systems_offline(*variables)
			search_thread = threading.Thread(target = t, \
							args = [[start_coords, end_coords, infile, self]])
		# Use a different function if online mode is activated.
		else:
			# All of what was written above is valid here, too.
			t = lambda variables: on.find_systems_online(*variables)
			search_thread = threading.Thread(target = t, \
							args = [[start_coords, end_coords, self]])

		# For being able to close a thread gracefully I need run it as a daemon.
		# See second option in answer here: https://stackoverflow.com/ ...
		# ... questions/25145278/root-destroy-does-not-terminate-threads-running-in-shell
		search_thread.daemon = True
		search_thread.start()

		# Once the search is finished, the result shall be saved. This 
		# requires another thread to not freeze the gui.
		t = lambda variables: self._save_information(*variables)
		save_thread = threading.Thread(target = t, args = [['searching_stars', \
								'stars', self.star_search_text, './stars']])
		save_thread.daemon = True
		save_thread.start()


	# The actions carried out when the < self.create_nodes_button > is pressed.
	def _create_the_nodes(self):
		# Don't do anything if there is no data to work with.
		if not os.path.isfile('./stars'):
			this = "ATTENTION: Could not find (relevant) stars file. "
			that = "Won't do anything."
			self.create_nodes_text.setText(this + that)
			return
		elif self.mother.neutron_boosting and not self.mother.neutron_file_ok:
			this = "ATTENTION: Neutron boosting is activated but the "
			that = "neutron-stars file couldn't be found or is older than 2 days.\n" 
			siht = "Please download the newest file it with the button above."
			self.create_nodes_text.setText(this + that + siht)
			return
		elif self.creating_nodes:
			this = "ATTENTION: A preparation is already ongoing. Pressing the "
			that = "button won't do anything."
			self.create_nodes_text.setText(this + that)
			return

		self.creating_nodes = True

		this = "Loading the stars file. This may take a while ..."
		self.create_nodes_text.setText(this)

		with open('./stars', 'rb') as f:
			self.stars = pickle.load(f)

		# I need to check just if neutron boosted is activated or not because
		# above I already break if the necessary file is not present.
		if self.mother.neutron_boosting:
			self.preparing_neutron_stars = True
			this = "Fetching neutron stars information ..."
			self.create_nodes_text.setText(this)

			# off.collect_neutron_information() puts the neutron star 
			# information directly into < self.neutron_stars >.
			t = lambda self: off.collect_neutron_information(self)
			fetch_neutron_stars_thread = threading.Thread(target = t, \
															args = [self])
			fetch_neutron_stars_thread.daemon = True
			fetch_neutron_stars_thread.start()

			# Give it some time to "settle".
			sleep(0.5)

		t = lambda: self._make_nodes()
		make_nodes_thread = threading.Thread(target = t, args = [])
		make_nodes_thread.daemon = True
		make_nodes_thread.start()

		sleep(0.5)

		# Once the creation of the nodes is finished, the result shall be saved. 
		# This requires another thread to not freeze the gui.
		t = lambda variables: self._save_information(*variables)
		save_thread = threading.Thread(target = t, args = [['creating_nodes', \
					'pristine_nodes', self.create_nodes_text, './all_nodes']])
		save_thread.daemon = True
		save_thread.start()


	# The target of the thread in _create_the_nodes() that actually makes the
	# nodes ... or well, that calls the outside function that actualy makes
	# the nodes.
	def _make_nodes(self):
		# Don't do anything if neutron boosting is activated but the 
		# neutron stars information is not ready, yet.
		while (self.mother.neutron_boosting and self.preparing_neutron_stars):
			if self.mother.exiting.is_set():
				return

			sleep(0.5)

		# Update the stars information with neutron star information if
		# necessary. This process is fast.
		if self.mother.neutron_boosting:
			this = "Updating relevant stars with neutron star information ..."
			self.create_nodes_text.setText(this)

			off.update_stars_with_neutrons(self.stars, self.neutron_stars)

		t = lambda self: af.create_nodes(self)
		create_nodes_thread = threading.Thread(target = t, args = [self])
		create_nodes_thread.daemon = True
		create_nodes_thread.start()


	# The actions carried out when the < self.pathfinding_button > is pressed.
	def _find_path(self):
		# Reset the results window, just in case that there already is something.
		self.results.setPlainText('')

		if not os.path.isfile('./all_nodes'):
			this = "ATTENTION: Could not find a file with information prepared "
			that = "for the pathfinding algorithm. Please press the button above."
			self.pathfinding_text.setText(this + that)
			return
		elif self.finding_path:
			this = "ATTENTION: The pathfinding algorithm is already ongoing. "
			that = "Pressing the button won't do anything."
			self.pathfinding_button.setText(this + that)
			return

		self.finding_path = True

		loading_thread = threading.Thread(target = self._load_files)
		loading_thread.daemon = True
		loading_thread.start()

		pathfinding_thread = threading.Thread(target = self._send_probes)
		pathfinding_thread.daemon = True
		pathfinding_thread.start()


	# If many stars are used, loading the nodes file may take a while. Thus it 
	# get's its own thread to not freeze the gui and this is the target 
	# function of said thread.
	def _load_files(self):
		this = "Loading information (this may take a while) ..."
		self.pathfinding_text.setText(this)

		with open('./all_nodes', 'rb') as f:
			self.pristine_nodes = pickle.load(f)

		# Just in case.
		if self.mother.exiting.is_set():
			return

		with open('./stars', 'rb') as f:
			self.stars = pickle.load(f)

		this = "Finished loading information."
		self.pathfinding_text.setText(this)


	# The target of the thread that actualy will do the pathfinding.
	# The name of this function is due to how the algorithm works :) .
	def _send_probes(self):
		# Wait until the proper information is ready
		while not self.pristine_nodes or not self.stars:
			if self.mother.exiting.is_set():
				return

			sleep(1)

		# It turned out that some of the information displayed to the user 
		# will get lost in the constant updating of user information if the
		# necessary files are loaded very fast. A short delay seems to fix this.
		sleep(1)

		this = "Searching for a path from start to end. This may take a while ..."
		self.pathfinding_text.setText(this)

		stars = self.stars
		pristine_nodes = self.pristine_nodes
		neutron_boosting = self.mother.neutron_boosting
		start_coords = self.mother.start_coords
		end_coords = self.mother.end_coords
		# < max_tries > is a remnant from earlier versions. It is somewhat 
		# useful and in the future I may make it adjustable but so far it is
		# set to 23 ... Hello future me: I guess you never really bothered to 
		# make this adjustable by the user.
		max_tries = self.mother.max_tries

		self.start_star, self.end_star = af.find_closest(stars, start_coords, end_coords)

		this = 'Start star: {}\n'.format(list(self.start_star.keys())[0])
		that = 'End star: {}'.format(list(self.end_star.keys())[0])
		self.pathfinding_text.setText(this + that)

		t = lambda variables: fr.find_path(*variables)
		finding_thread = threading.Thread(target = t, args = [[max_tries, stars, \
								self.start_star, self.end_star, pristine_nodes, \
								neutron_boosting, self]])
		finding_thread.daemon = True
		finding_thread.start()

		counter_thread = threading.Thread(target = self._counter, args = [])
		counter_thread.daemon = True
		counter_thread.start()


	# Since the pathfinding algorithm needs some time in which seemingly 
	# nothing is happening, I'll display a counter to the user so that he or 
	# she doesn't think the program crashed.
	def _counter(self):
		i = 0
		while self.finding_path:
			i += 1
			if self.mother.exiting.is_set():
				return

			try:
				text = self.pathfinding_text.text().split('and counting ...\n')[1]
			except IndexError:
				text = self.pathfinding_text.text()

			this = "This will take a while! But as long as I'm counting, the "
			that = "program is still running and has NOT crashed! "
			siht = "Counter is at {} and counting ...\n".format(i)
			self.pathfinding_text.setText(this + that + siht + text)

			sleep(1)


	# The method that will print the results once the pathfinding algorithm is
	# finished. To get this printing into a QPlainTextEdit instance done is 
	# more complicated and the whole reason for the signal -> slot stuff as 
	# described in the very beginning of this class definition.
	def _print_results(self):
		start_star = list(self.start_star.keys())[0]
		end_star = list(self.end_star.keys())[0]

		this = "Start at: {}\n  End at: {}\n\n".format(start_star, end_star)
		that = "Number of stars considered: {}\n\n".format(len(self.stars))
		text = this + that

		this = 'Format of results: < starname >   =>   < ly from previous star > '
		that = '   =>   < jumptype from previous star >\nFormat of jumptype: '
		siht = '< B#(F) > with B = boosted, # = grade of boost, (F) = on fumes '
		taht = '(displayed just if jump is on fumes)'
		text = text + this + that + siht + taht

		if self.mother.neutron_boosting:
			this = "\n\nATTENTION: Neutron boosted jumps are enabled BUT you need "
			that = "to make sure for yourself that you DON'T RUN OUT OF FUEL!\n\n"
			text = text + this + that

		text = text + af.print_jumper_information(self.fewest_jumps_jumper, self)

		if self.mother.neutron_boosting:
			if not self.way_back_jumper:
				this = "\nATTENTION: Neutron jumping may allow you to get to your "
				that = "goal BUT no way back could be found.\nHowever, you may still "
				siht = "be able to find a way manually since not all systems are "
				taht = "registered in the database."
				text = text + this + that + siht + taht
			else:
				this = "\nYou will be able to get back. Below is ONE possible way back.\n"
				that = af.print_jumper_information(self.way_back_jumper, self)
				text = text + this + that

		self.results.setPlainText(text)






















