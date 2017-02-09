import os
 
def addGizmos(path, menuMain=None):
	m = menuMain.addMenu("Jellyfish")
	for root, dirs, files in os.walk(path):
		for fileNameCompl in files:
			fileName, fileExt = os.path.splitext(fileNameCompl)
			if fileExt == ".gizmo":
				#print fileName
				folder = (root + "/")[len(path)+1:]
				m.addCommand(folder + fileName, "nuke.createNode('" + fileName + "')")