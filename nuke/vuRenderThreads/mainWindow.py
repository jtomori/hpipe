#	-----------------------------------------------------------------------------
#	This source file has been developed by Vincent Ullmann within the scope of the
#	Technical Director course at Filmakademie Baden-Wuerttemberg.
#	http://td.animationsinstitut.de/
#
#	Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#	-----------------------------------------------------------------------------

import sys, os
import re
from PySide import QtGui, QtCore # Should be in PythonPath from Nuke

# vuRenderThreads
import checkThread
import style
import listItem



def parseProgress(text):
	template = "Frame (?P<frame>\d+)\ \((?P<curFrame>\d+)\ of (?P<totalFrames>\d+)\)"
	matches = re.finditer(template, text)
	for match in matches:
		match = match.groupdict()
		return {k:int(v) for (k,v) in match.iteritems()}
	return None


def buildTitle():
	# Set Title:
	title = ""
	title += " | " + os.getenv("DCC")
	title += " | " + os.path.basename(os.getenv("SCENE"))
	title += " | " + os.getenv("WRITENODES")
	return title




class MainWindow(QtGui.QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.threads = []
		self.widgets = []
		self.threadLists = {}	# Dict to store QListWidgets


		# Widget: OutPut
		self.out = QtGui.QPlainTextEdit()
		self.out.setReadOnly(True)
		self.out.setWordWrapMode(QtGui.QTextOption.NoWrap)

		outLayout = QtGui.QVBoxLayout()
		outLayout.setContentsMargins(0, 0, 0, 0)
		outLayout.addWidget(QtGui.QLabel("Output:"))
		outLayout.addWidget(self.out)
		outWidget = QtGui.QWidget()
		outWidget.setLayout(outLayout)


		# Widget: Threads
		threadsLayout = QtGui.QVBoxLayout()
		threadsLayout.setContentsMargins(0, 0, 0, 0)
		threadsLayout.addWidget(QtGui.QLabel("Threads:"))
		self.threadList = QtGui.QListWidget()
		threadsLayout.addWidget(self.threadList)

		threadsWidget = QtGui.QWidget()
		threadsWidget.setLayout(threadsLayout)


		# Layout: Splitter
		splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		splitter.addWidget(threadsWidget)
		splitter.addWidget(outWidget)

		# Layout: Main
		self.layout = QtGui.QHBoxLayout()
		self.setLayout(self.layout)
		self.layout.addWidget(splitter)


		self.connect(self.threadList, QtCore.SIGNAL("currentRowChanged(int)"), self.changeThread)



		self.setStyleSheet(style.STYLE)
		self.setWindowTitle("vuRenderThreads: " + buildTitle())
		self.resize(960, 360)
		self.show()


	def updateSelection(self, num):
		for widget in self.widgets:
			widget.setSelected(False)
		self.widgets[num].setSelected(True)


	def changeThread(self, num):

		# Set selection live
		for t in self.threads:
			t.isLive = False
		self.currentThread = self.threads[num]
		self.currentThread.isLive = True


		self.updateSelection(num)
		self.thread_updateOut(self.currentThread)

		# Auto Scroll to End (if not in focus)
		if not self.out.hasFocus():
			scrollBar = self.out.verticalScrollBar()
			scrollBar.setValue(scrollBar.maximum())



	def thread_updateOut(self, thread):
		#print "thread_updateOut"
		#value = thread.text
		value = thread.outText

		#value = "<p>" + value
		#value = value.replace("\n", "<br>")
		#value = value.replace("Frame", "<font color='DeepSkyBlue '>Frame</font>")
		msg = ""
		msg += "_" * 8 + thread.text + " Output" + "_" * 8
		msg +=  "\n"*3

		self.out.setPlainText(msg + value)
		#self.out.appendHtml(value)
		pass



	def thread_updateProgress(self, item, text):
		values = parseProgress(text)

		if values:
			msg = "Frame %d ( %d of %d )" % (values["frame"], values["curFrame"], values["totalFrames"])
			item.setProgress(values["curFrame"], msg)
			item.setMaximum(values["totalFrames"])


	def thread_finished(self, item, thread, value):
		if value == 0:
			item.setProgressDone()
		else:
			item.setProgressError()


	def addThread(self, thread, threadName="Thread"):

		# Add to ListWidget
		widget = listItem.createListItem(self.threadList, threadName)
		self.threads += [thread]
		self.widgets += [widget]

		# Connect
		def thread_updateProgress_thisThread(text):
			self.thread_updateProgress(widget, text)
		thread.signal_updateProgress.connect(thread_updateProgress_thisThread)

		def thread_finished_thisThread(value):
			self.thread_finished(widget, thread, value)
		thread.signal_finished.connect(thread_finished_thisThread)

		def thread_updateOut_thisThread():
			self.thread_updateOut(thread)
		thread.signal_updateOutput.connect(thread_updateOut_thisThread)

		return widget


	def addSpacer(self, name=""):
		#item = self.threadList.addItem(name)
		widget = QtGui.QWidget()
		widget.setStyleSheet("border: 1px solid red")

		listWidgetItem = QtGui.QListWidgetItem(name)
		self.threadList.addItem(listWidgetItem)
		self.threadList.setItemWidget(listWidgetItem, widget)



	def closeEvent(self, event):
		for t in self.threads:
			t.close()


	def createCheckThread(self):
		self.checkThread = checkThread.CheckThread(self.threads)
		self.checkThread.start()
		self.checkThread.signal_done.connect(self.showMsg)


	def showMsg(self):
		msgBox = QtGui.QMessageBox()
		msgBox.setWindowFlags(msgBox.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		msgBox.setText("vuRenderThreads:\nI'm done with this shit")
		msgBox.exec_()



