#    "gap_jumper" (v2.0)
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

print("Loading necessary modules ...")

from sys import exit
# In pyqt4 QApplication was in QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import motherwindow as mw


app = QApplication([])

main = mw.Motherwindow(app)

# This here is just to be able to use CTRL + C on the shell to close the gui.
# See here: https://machinekoder.com/how-to-not-shoot-yourself-in- ...
# ... the-foot-using-python-qt/
timer = QTimer()
timer.timeout.connect(lambda: None)
timer.start(500)


exit(app.exec_())






















