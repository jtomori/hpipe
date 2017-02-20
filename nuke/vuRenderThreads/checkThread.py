#	-----------------------------------------------------------------------------
#	This source file has been developed by Vincent Ullmann within the scope of the
#	Technical Director course at Filmakademie Baden-Wuerttemberg.
#	http://td.animationsinstitut.de/
#
#	Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#	-----------------------------------------------------------------------------

from PySide import QtGui, QtCore # Should be in PythonPath from Nuke
import time

class CheckThread(QtCore.QThread):
	signal_done = QtCore.Signal()

	def __init__(self, threadList=[], parent=None):
		super(CheckThread, self).__init__(parent)
		self.threadList = threadList


	def run(self):
		while True:
			time.sleep(0.2)
			if all(t.done for t in self.threadList):
				self.signal_done.emit()
				return True

			# Force Updates
			for t in self.threadList:
				t.readOutput()

