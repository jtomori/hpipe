#!/bin/python

#	-----------------------------------------------------------------------------
#	This source file has been developed by Vincent Ullmann within the scope of the
#	Technical Director course at Filmakademie Baden-Wuerttemberg.
#	http://td.animationsinstitut.de/
#
#	Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#	-----------------------------------------------------------------------------

import sys, os

#ROOT_HOU = "C:/Program Files/Side Effects Software/Houdini 15.0.244.16"
#sys.path.append(ROOT_HOU + "/python27/lib/site-packages-ui-forced")
#os.environ["PATH"]			= ROOT_HOU + "/python27/lib/site-packages-ui-forced/PySide;" + str(os.getenv("PATH"))

from PySide import QtGui, QtCore # Should be in PythonPath from Nuke
#from PyQt4 import QtGui, QtCore # Should be in PythonPath from Nuke

# vuRenderThreads
import mainWindow
import renderThread


def createThreads(window):
	# Get Vars
	writeNodes	= eval(os.getenv("WRITENODES"))
	frameStart	= int(os.getenv("frameStart"))
	frameEnd	= int(os.getenv("frameEnd"))
	numThreads	= int(os.getenv("numThreads"))

	# Build Threads
	for nodeName in writeNodes:
		for threadNum in range(numThreads):
			thread	= renderThread.RenderThread(threadNum, numThreads, frameStart, frameEnd, nodeName)
			widget	= window.addThread(thread, "%s | #%d/%d" % (nodeName, threadNum+1, numThreads))
			thread.render()


def main():
	app = QtGui.QApplication([])


	# Build Window
	window = mainWindow.MainWindow()

	createThreads(window)
	window.createCheckThread()

	app.exec_()




if __name__ == '__main__':

	#TMP = "D:/Vincent/svn/vuRenderThreads/plugin_houdini/renderScript.py"
	# DEBUG Vars
	#os.environ["DCC"]			= "houdini"
	#os.environ["EXE"]			= TMP
	#os.environ["SCENE"]			= "D:/Vincent/svn/vuRenderThreads/plugin_houdini/test.hip"
	#os.environ["WRITENODES"]	= "['/out/geo1']"
	#os.environ["frameStart"]	= "1"
	#os.environ["frameEnd"]		= "2000"
	#os.environ["numThreads"]	= "2"
	main()