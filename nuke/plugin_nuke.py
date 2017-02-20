#	-----------------------------------------------------------------------------
#	This source file has been developed by Vincent Ullmann within the scope of the
#	Technical Director course at Filmakademie Baden-Wuerttemberg.
#	http://td.animationsinstitut.de/
#
#	Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#	-----------------------------------------------------------------------------

import os, sys, subprocess
import nuke


ROOT_NUKE	= os.path.dirname(os.path.abspath(nuke.EXE_PATH))
#ROOT_RT		= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_RT		= "F:\\00_pipeline\\nuke\\vuRenderThreads"


def setEnvoriment():
	sep = ";" if sys.platform == "win32" else ":"

	os.environ["PYTHONPATH"]	= ROOT_NUKE + "/pythonextensions/site-packages" + sep + str(os.getenv("PYTHONPATH"))
	os.environ["PATH"]			= ROOT_NUKE + sep + str(os.getenv("PATH"))



def createOutfolder(node):

	if type(node) == str:
		node = nuke.toNode(node)


	knob = node["file"]

	if not knob:
		return False


	folder = os.path.dirname(knob.value())
	folder = folder.replace("N:/", "/bigfoot/kroetenlied/")

	if not os.path.isdir(folder):
		os.makedirs(folder)
		return True




WRITENODES = ["Write"] + ["Jagon_Write_v003", "J_WriteUndistort", "Flut_Write", "Kryo_Write", "Kroeten_Write", "vuWrite"]

def getWriteNodes():
	# Check Selection
	if len(nuke.selectedNodes()) == 0 :
		nodes = nuke.allNodes()
	else:
		nodes = nuke.selectedNodes()

	writeNodes = []
	for oNode in nodes:
		if oNode.Class() in WRITENODES and (False == oNode["disable"].value()):
			writeNodes += [oNode.name()]

	return writeNodes



def createThreads(frameStart, frameEnd, numThreads, writeNodes=None):
	nuke.scriptSave()

	if not writeNodes:
		writeNodes = getWriteNodes()

	# Create Folders
	for writeNode in writeNodes:
		try:
			createOutfolder(writeNode)
		except:
			pass



	os.environ["DCC"]			= "nuke"
	os.environ["EXE"]			= nuke.EXE_PATH
	os.environ["SCENE"]			= nuke.root().name()
	os.environ["WRITENODES"]	= str(writeNodes)

	os.environ["frameStart"] 	= str(frameStart)
	os.environ["frameEnd"]		= str(frameEnd)
	os.environ["numThreads"]	= str(numThreads)


	# Start
	setEnvoriment()
	os.chdir(ROOT_RT)

	if sys.platform == "win32":
		print os.startfile("main.bat")
	else:
		opener ="open" if sys.platform == "darwin" else "xdg-open"
		subprocess.call(["bash", "main.sh"])


def showPopup():

	# Get some Defaults:
	frameStart	= nuke.value('root.first_frame')
	frameEnd	= nuke.value('root.last_frame')

	for node in nuke.selectedNodes():
		try:
			if node["use_limit"].value():
				frameStart	= int(node["first"].value())
				frameEnd	= int(node["last"].value())
		except Exception, e:
			pass




	# Create Popup
	p = nuke.Panel("Batch Render Threads")
	p.addSingleLineInput("First Frame:",	frameStart)
	p.addSingleLineInput("Last Frame:",		frameEnd)
	p.addSingleLineInput("Threads:",		"8")

	p.addButton("Cancel")
	p.addButton("OK")
	p.setWidth(200)
	result = p.show()


	if result == 1:
		frameStart	= p.value("First Frame:")
		frameEnd	= p.value("Last Frame:")
		numThreads	= p.value("Threads:")
		createThreads(frameStart, frameEnd, numThreads)
	else:
		print "Canceled!"


def main():
	showPopup()