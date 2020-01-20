#    "motherwindow" (v2.0)
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

# This file contains the class definition of the main (and only) window of 
# the gui. The gui contains two "layers". One for user input and one for the 
# actual work this program shall do to be done.

from PyQt5.QtWidgets import QWidget, QStackedLayout

import screen_input as si
import screen_work as sw
import threading


# The class definition of the main window. It contains the attributes that
# need to be available in both layers.
class Motherwindow(QWidget):
	def __init__(self, app):
		super(Motherwindow, self).__init__()
		self.destroyed.connect(lambda: print("foo"))
		self.app = app
		self.jumpable_distances = None
		self.start_coords = None
		self.end_coords = None
		self.neutron_boosting = False
		self.neutron_file_ok = False
		# Which mode shall be used to search for relevant stars.
		# In screen_input.py the buttons are radio buttons. Thus just one 
		# is activated at any time. Thus it is enough to "monitor" the state
		# of the button of of one of the online/offline modes. I decided to 
		# take the offline mode, since this is the default behaviour.
		self.offline_mode = True
		# This is the complete systemsWithCoordinates.json-file!
		self.starsfile = None
		# This is the files that contains JUST the stars in the cylinder from
		# start to end.
		self.stars = None
		# If a new run with different parameters (e.g. jumprange) but the 
		# same start- and end-coordinates shall be done. In that case it is not 
		# necessary to go through the systemsWithCoordinates-file again.
		self.cached = False
		# < max_tries > is a remnant from earlier versions. It is somewhat 
		# useful and in the future I may make it adjustable but so far it is
		# set to 23.
		self.max_tries = 23

		# In < screen_work > several separate threads are started. These will 
		# continue running even if the gui is closed. Thus I need to modify the 
		# closing procedure of the gui.
		# Basically I just set an attribute of the Motherwindow instance and
		# all the threads check if it is set and stop executing if it is.

		# See here: https://srinikom.github.io/pyside-docs/PySide/QtGui/QCloseEvent.html
		self.exiting = threading.Event()

		self._initUI()


	# I need to change the method that is called when the program is closed.
	# To take care of any running separate thread. See also comment above 
	# regarding this issue.
	# < event > will be automatically filled with a QCloseEvent when the 
	# X-button is pressed for closing the window
	def closeEvent(self, event):
		self.exiting.set()
		self.close()


	# This function instantiates the two layers and exists just to keep 
	# __init__() more tidy.
	def _initUI(self):
		self.setGeometry(50, 50, 10, 10)
		self.stacked_layout = QStackedLayout()

		self.screen_input = si.ScreenInput(self, 50, 50)
		self.stacked_layout.insertWidget(0, self.screen_input)

		self.screen_work = sw.ScreenWork(self, 50, 50)
		self.stacked_layout.insertWidget(1, self.screen_work)
		self.stacked_layout.setCurrentIndex(0)






















