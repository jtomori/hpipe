#	-----------------------------------------------------------------------------
#	This source file has been developed by Vincent Ullmann within the scope of the
#	Technical Director course at Filmakademie Baden-Wuerttemberg.
#	http://td.animationsinstitut.de/
#
#	Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#	-----------------------------------------------------------------------------

import os, sys
from PySide import QtGui, QtCore


# SETTINGS
CMD_TEMPLATE = {}
CMD_TEMPLATE["nuke"]    = '"%(EXE)s" -i -X %(NODE)s -F %(fStart)s-%(fEnd)sx%(fStep)s "%(SCENE)s"'
CMD_TEMPLATE["houdini"] = 'hython.exe %(EXE)s %(SCENE)s %(NODE)s %(fStart)s %(fEnd)s %(fStep)s'



class RenderThread(QtCore.QProcess):
	signal_updateProgress	= QtCore.Signal(str)
	signal_updateOutput		= QtCore.Signal(str)
	signal_finished			= QtCore.Signal(int)

	"""docstring for RenderThread"""
	def __init__(self, threadNum, numThreads, frameStart, frameEnd, nodeName, parent=None):
		super(RenderThread, self).__init__(parent=None)


		# Values
		self.outText = ""
		self.text = nodeName + " | #" + str(threadNum+1) + " / " + str(numThreads) + " | "

		# Flags
		self.isLive	= False		# If true emit QtSignal for Updates
		self.done	= False
		self.failed = False		# If true be Red



		# Connections
		self.finished.connect(self.renderFinished)
		self.setProcessChannelMode(QtCore.QProcess.MergedChannels)
		self.readyReadStandardOutput.connect(self.readOutput)
		self.readyRead.connect(self.readOutput)

		# Copy Env
		self.setProcessEnvironment(QtCore.QProcessEnvironment.systemEnvironment())



		# Build Command
		template = CMD_TEMPLATE[os.environ["DCC"]]

		values = {}
		values["EXE"]		= os.environ["EXE"]
		values["SCENE"]		= os.environ["SCENE"]
		values["NODE"]		= nodeName
		values["fStart"]	= str(frameStart + threadNum)
		values["fEnd"]		= str(frameEnd)
		values["fStep"]		= str(numThreads)

		self.cmd = template % values



	def render(self):
		self.start(self.cmd)


	def readOutput(self):
		text = str(self.readAllStandardOutput())
		self.outText += text

		if self.isLive:
			self.signal_updateOutput.emit(text)

		# Get Last Update-Line
		lines = text.split("\n")[:-1]		# rmeove last line, becouse it might be incomplete
		for line in reversed(lines):
			if line.startswith("Frame"):
				self.signal_updateProgress.emit(text)
				return



	def renderFinished(self):
		"""
		ERROR_KEYWORDS = ["ERROR", "denied", "Read error"]

		for keyword in ERROR_KEYWORDS:
			if keyword in text:
				self.setProgress_Error()
				self.failed = True
		"""

		self.signal_finished.emit(self.exitCode())
		self.done = True


