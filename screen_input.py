#    "screen_input" (v2.0)
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

# This file contains the class definition of the user input layer of the main 
# (and only) window of the gui. 

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpacerItem, QCheckBox, QRadioButton, QButtonGroup
import os
import additional_functions as af


# The class definition of the the user input layer of the main window.
class ScreenInput(QWidget):
	# < mother > is the main window instance that actually instantiates this 
	# class.
	def __init__(self, mother, x_position, y_position):
		super(ScreenInput, self).__init__()
		self.mother = mother
		# These are the only two attributes that need to be stored for 
		# further use.
		self.jumprange = None
		self.on_fumes = None

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
		self.setGeometry(x_position, y_position, 1000, 10)
		self.layout = QGridLayout()
		self.setLayout(self.layout)

		spacer = QSpacerItem(23, 23)

		# First the jumprange stuff, ...
		self.jumprange_input = QLineEdit()
		self.layout.addWidget(QLabel("Jumprange in ly:"), 1, 0)
		self.layout.addWidget(self.jumprange_input, 1, 1)

		self.on_fumes_input = QLineEdit()
		self.on_fumes_input.setPlaceholderText("Leave empty if you don't know it.")
		self.layout.addWidget(QLabel("Jumprange on fumes in ly:"), 2, 0)
		self.layout.addWidget(self.on_fumes_input, 2, 1)

		# ... then, the start- and end-coordinates stuff, ...
		self._make_coordinates_input_fields()

		# ... then, the neutron boost checkbox, ...
		self.layout.addWidget(QLabel("Use Neutron boosts:"), 12, 0)
		self.neutron_boost_box = QCheckBox("(Checked means YES.)")
		self.layout.addWidget(self.neutron_boost_box, 12, 1)

		# ... followed by all the necessary things for online/offline search 
		# (the latter is the default), and ...
		self._make_offline_online_mode_stuff()

		# ... the last user input is the "use cached stars"-stuff.
		self._make_cached_mode_stuff()

		# Some spacers for better looks, ...
		self.layout.addItem(spacer, 3, 0)
		self.layout.addItem(spacer, 7, 0)
		self.layout.addItem(spacer, 11, 0)
		self.layout.addItem(spacer, 13, 0)
		self.layout.addItem(spacer, 17, 0)

		# ... the continue button, ...
		self.continue_button = QPushButton('Continue')
		self.continue_button.clicked.connect(self._continue_action)
		self.layout.addWidget(self.continue_button, 24, 0)

		# ... and the messages to the user in the end.
		self.layout.addWidget(QLabel("(Error) Messages"), 26, 0)
		self.messages = QLabel()
		self.layout.addWidget(self.messages, 26, 1)


	# Here follow all the methods that actually create the stuff to be shown
	# on screen.

	# Just to keep _initUI() more tidy.
	def _make_coordinates_input_fields(self):
		these = ["x", "y", "z"]
		for i in range(len(these)):
			self.layout.addWidget(QLabel("Start {} Coordinate:".format(these[i])), i + 4, 0)
			setattr(self, 'start_{}_input'.format(these[i]), QLineEdit())
			self.layout.addWidget(getattr(self, 'start_{}_input'.format(these[i])), i + 4, 1)

		# If the tab-key is used to go to the next input field the cursor will 
		# end up in the next field that was put into < self.layout >.
		# Thus, if all would be done in just the above loop, the cursor would 
		# jump between start- and end-coordinates.
		for i in range(len(these)):
			self.layout.addWidget(QLabel("End {} Coordinate:".format(these[i])), i + 8, 0)
			setattr(self, 'end_{}_input'.format(these[i]), QLineEdit())
			self.layout.addWidget(getattr(self, 'end_{}_input'.format(these[i])), i + 8, 1)


	# Dito
	def _make_offline_online_mode_stuff(self):
		# ATTENTION: If the stars shall be looked for offline, the 
		# systemsWithCoordinates-file must be provided. To tell the user this, 
		# the placeholder_1 text in the file input field will be changed depending
		# on the state of the radio button(s). However, to be able to change 
		# this text the field need to be known and thus need to be defined
		# before the buttons, even though it appears after said buttons.
		# This messes a bit with the position in the layout.
		self.open_file_button = QPushButton("Open Coordinates file")
		# QFileDialog.getOpenFileName() returns a tuple. The second variable
		# in it is the filter for which files shall be looked for in the 
		# filedialog. Since I don't use this option I discard it.
		self.open_file_button.clicked.connect(lambda: \
			self.offline_file_input.setText(QFileDialog.getOpenFileName()[0]))
		self.layout.addWidget(self.open_file_button, 16, 0)

		self.offline_file_input = QLineEdit()
		this = "Provide the systemsWithCoordinates-file or have it in the "
		that = "installation directory."
		placeholder_1 = this + that
		self.offline_file_input.setPlaceholderText(placeholder_1)
		self.layout.addWidget(self.offline_file_input, 16, 1)

		# The first radio button ...
		self.layout.addWidget(QLabel("Use OFFline mode"), 14, 0)
		text = "(Recommended; if checked provide systemsWithCoordinates-file below.)"
		self.offline_mode = QRadioButton(text)
		self.offline_mode.setChecked(True)
		self.offline_mode.toggled.connect(lambda: \
						self.offline_file_input.setPlaceholderText(placeholder_1))

		# ... and the second radio button.
		self.layout.addWidget(QLabel("Use ONline mode"), 15, 0)
		placeholder_2 = 'Any input here will be ignored.'
		self.online_mode = QRadioButton()
		self.online_mode.toggled.connect(lambda: \
						self.offline_file_input.setPlaceholderText(placeholder_2))

		# The radiobuttons need to be in a group so that selecting one 
		# deselects the other.
		self.button_group = QButtonGroup()
		self.button_group.addButton(self.offline_mode)
		self.button_group.addButton(self.online_mode)

		# Don't add < self.button_group > but the buttons themself!
		self.layout.addWidget(self.offline_mode, 14, 1)
		self.layout.addWidget(self.online_mode, 15, 1)


	# Dito
	def _make_cached_mode_stuff(self):
		self.layout.addWidget(QLabel("Use Cached stars:"), 18, 0)
		this = "(Checked means YES. Press button below to learn what that means.)"
		self.cached_box = QCheckBox(this)
		self.layout.addWidget(self.cached_box, 18, 1)

		self.wtf_button = QPushButton("WTF does that mean?")
		self.wtf_button.clicked.connect(self._display_cached_description)
		self.layout.addWidget(self.wtf_button, 19, 1)


	# Just to keep _make_cached_mode_stuff() more tidy.
	def _display_cached_description(self):
		_1 = "Looking up the relevant stars takes some time. Thus, "
		_2 = "the result of the star-search are saved in the file called "
		_3 = "'stars' (no extension).\nIf you now want to find a route for the "
		_4 = "same start- and end-points but with different parameters (either "
		_5 = "a larger jump range, or with neutron boosting allowed, or both) "
		_6 = "check the box.\nIn this case the program will use said 'stars'-"
		_7 = " file and one has not to wait for the relevant stars to be found.\n"
		_8 = "\nATTENTION: The information for the pathfinding algorithm needs "
		_9 = "to be prepared again, since the parameters changed!"

		text = _1 + _2 + _3 + _4 + _5 + _6 + _7 + _8 + _9
		self.messages.setText(text)


	# Here follow the definitions of what to check and the of the actions to be 
	# undertaken (incl. said checks) once the continue button was pressed.
	# ATTENTION: checking the user input for errors directly sets the respective
	# values if no error occurs. So the method names are a bit misleading but I 
	# didn't want to make them overly long.

	# This method is just to keep _continue_action() more tidy. It "grabs" 
	# the jumprange provided by the user in the input field and returns True
	# if sth. is wrong with the information.
	def _jumprange_error(self):
		try:
			jumprange = float(self.jumprange_input.text().replace(',', '.'))
		except ValueError:
			# For the case that the user get's the jumprange right once, but 
			# sth. different wrong and when trying again the jumprange is 
			# wrong, too. In that case < self.jumprange > needs to be resetted.
			self.jumprange = None
			return True

		# The algorithm doesn't work with the jumprange directly but rather
		# needs all jumpranges for all possible boosting grades. This is
		# calculated afterwards but for this the jumprange value needs to be
		# stored.
		if jumprange > 0:
			self.jumprange = jumprange
		else: 
			return True


	# Dito but for the jumprange on fumes.
	def _on_fumes_error(self):
		on_fumes = None

		# If a user doesn't know the jumprange on fumes, just a small value
		# shall be added.
		# < self.jumprange > could be None; usually of there is an error
		# in the jumprange input.
		if self.jumprange and not self.on_fumes_input.text():
			on_fumes = self.jumprange + 0.01

		try:
			if not on_fumes:
				on_fumes = float(self.on_fumes_input.text().replace(',', '.'))
		except ValueError:
			return True

		if on_fumes >= self.jumprange:
			self.on_fumes = on_fumes
		else: 
			return True


	# More or less dito but for the start and end coordinates.
	def _coordinates_error(self):
		self.mother.start_coords = {}
		self.mother.end_coords = {}

		for this in ["x", "y", "z"]:
			try:
				field = getattr(self, 'start_{}_input'.format(this))
				value = float(field.text().replace(',', '.'))
				self.mother.start_coords[this] = value

				field = getattr(self, 'end_{}_input'.format(this))
				value = float(field.text().replace(',', '.'))
				self.mother.end_coords[this] = value
			except ValueError:
				return True


	# More or less dito, but for the systemsWithCoordinates-file for 
	# offline mode.
	def _file_error(self):
		if self.offline_mode.isChecked():
			self.mother.starsfile = None

			infile = self.offline_file_input.text().strip()

			# First check if the user has provided a file ...
			if infile:
				# ... and if that actually is a file.
				if os.path.isfile(infile):
					self.mother.starsfile = infile
					return
			# If that is not the case ... 
			else:
				# ... check if the file with the default name is already in the 
				# working directory.
				if os.path.isfile('./systemsWithCoordinates.json'):
					self.mother.starsfile = './systemsWithCoordinates.json'
					return

			# If none of the above cases check out, it is obviously an user 
			# input error.
			return True


	# Dito but for a cached stars-file.
	def _cached_file_error(self):
		self.mother.cached = self.cached_box.isChecked()

		if self.cached_box.isChecked() and not os.path.isfile('./stars'):
			return True
		elif self.cached_box.isChecked():
			this = "The cached stars-file will be used."
			self.mother.screen_work.star_search_text.setText(this)
			self.mother.screen_work.star_search_button.hide()


	# Finally, the definition of all the stuff that needs to be done, when the 
	# continue-button was pressed ... who would have thought that.
	# ATTENTION: Here just a few values are set, since this often happens 
	# already when checking for user input error as defined in the methods 
	# above.
	def _continue_action(self):
		self.messages.setText('')

		if self._input_error():
			return

		# ATTENTION: The very first value MUST be zero! This is because of how 
		# the actual pathfinding algorithm works. The last value is for neutron 
		# boosted jumps.
		self.mother.jumpable_distances = [0] + [x*y for 
							x in [1, 1.25, 1.5, 2.0] for \
							y in [self.jumprange, self.on_fumes]] + \
							[self.jumprange * 4]

		# Check if neutron boosting is activated ...
		self.mother.neutron_boosting = self.neutron_boost_box.isChecked()

		# ... and do different things on the next screen for different 
		# conditions.
		if self.neutron_boost_box.isChecked() and not af.neutron_file_ok():
			# If the back button of the next screen was pressed while the 
			# neutron-stars filewas downloading, don't do anything. If the 
			# download finished while being back at this screen, af.neutron_file_ok()
			# will return True and the file does not need to be downloaded again.
			# I admit that this is a very constructed case, but it happened 
			# during testing. Under normal operation, the if condition will
			# always trigger.
			if not self.mother.screen_work.downloading_neutron_file:
				this = "Neutron boosting shall be used. For this the newest "
				that = "< neutron-stars.csv > file (ca. 50 MB) needs to be "
				siht = "downloaded from edastro.com. Pressing the button does "
				taht = "that for you.\nOr download the file yourself, put it "
				more = "into the installation directory and skip this step."
				text = this + that + siht + taht + more

				self.mother.screen_work.neutron_text.setText(text)
				self.mother.screen_work.neutron_text.show()
				self.mother.screen_work.download_neutron_file_button.show()
		elif self.neutron_boost_box.isChecked() and af.neutron_file_ok():
			this = "Neutron boosted jumps are activated and the neutron-stars "
			that = "file is up to date and does not need to be downloaded."
			self.mother.screen_work.neutron_text.setText(this + that)
			self.mother.screen_work.neutron_text.show()
			self.mother.screen_work.download_neutron_file_button.hide()
			self.mother.neutron_file_ok = True

		# Set which mode to find the relevant stars shall be used.
		self.mother.offline_mode = self.offline_mode.isChecked()

		# This seems unnecessary, BUT the labels that belong to certain buttons 
		# in the next layer change when said  button is pressed. This is usually 
		# connected to certain tasks being carried out and said labels update 
		# according to how far the process came. Thus, if the user presses the 
		# back button of the next screen to change some parameters, and said 
		# processes finish while the user is on this screen, these labels must
		# show something meaningful again.
		if not self.mother.screen_work.searching_stars and not self.mother.cached:
			this = "Press the button below to start the search for relevant "
			that = "stars. This will take a while!"
			self.mother.screen_work.star_search_text.setText(this + that)

		if not self.mother.screen_work.creating_nodes:
			this = "Press the button below to prepare the information for the "
			that = "pathfinding algorithm\nUsually AFTER the relevant stars were "
			siht = "found or if chached stars are used.\nThis may take a while!"
			self.mother.screen_work.create_nodes_text.setText(this + that + siht)

		if not self.mother.screen_work.finding_path:
			this = "AFTER the information was prepared, press the button below to "
			that = "start the pathfinding algorithm. This will take a while!"
			self.mother.screen_work.pathfinding_text.setText(this + that)


		# And in the end, switch to the next layer (or screen).
		self.mother.stacked_layout.setCurrentIndex(1)


	# Just to keep _continue_action() more tidy.
	def _input_error(self):
		error = ''

		# Grab the jumprange ...
		if self._jumprange_error():
			this = 'ATTENTION: Jumprange must be a number and larger than zero!\n\n'
			error = error + this

		# ... and the jumprange on fumes.
		if self._on_fumes_error():
			this = 'ATTENTION: Jumprange on fumes must be a number and larger '
			that = 'than regular jumprange.\n\n'
			error = error + this + that

		# Grab the coordinates.
		if self._coordinates_error():
			this = 'ATTENTION: The Start/End-Coordinates must be numbers!\n\n'
			error = error + this

		# If offline mode is used, get the systemsWithCoordinates-file.
		if self._file_error():
			this = "ATTENTION: Provide the < systemsWithCoordinates.json > "
			that = "file or chose online mode.\n\n"
			error = error + this + that

		if self._cached_file_error():
			this = 'ATTENTION: "Use cached stars" was chosen but no cached '
			that = 'stars are available.\nThe program must run once with the '
			siht = 'desired start- and end-coordinates so that the correct '
			taht = 'stars can be cached.\nUNCHECK this option!'
			error = error + this + that + siht + taht

		if error:
			self.messages.setText(error)
			return True






















