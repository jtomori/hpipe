'''
hpipe - collection of useful functions
base for houdini pipeline
created by Juraj Tomori
'''

import glob, os, json
import hou

# shot name template: s010_shotName_fx_cloudSetup_jtomori_v001.hipnc
# asset name template: fx_cloudRig_jtomori_v001.hipnc
# initializes global variables in houdini session
def initVars():
	hipname = hou.getenv('HIPNAME')
	if hipname != 'untitled':
		attribs = hipname.split("_")
		if len(attribs) == 6:
			hou.putenv('SHOT', attribs[0])
			hou.putenv('SHOTNAME', attribs[1])
			hou.putenv('TASK', attribs[2])
			hou.putenv('TASKNAME', attribs[3])
			hou.putenv('USER', attribs[4])
			hou.putenv('VER', attribs[5])
		elif len(attribs) == 4:
			hou.putenv('TASK', attribs[0])
			hou.putenv('ASSET', attribs[1])
			hou.putenv('USER', attribs[2])
			hou.putenv('VER', attribs[3])
		elif len(attribs) > 0:
			hou.putenv('VER', attribs[-1])

# splits versioning string into letter and number, e.g. v025 -> ['v','025']
def verSplit(ver):
	head = ver.rstrip('0123456789')
	tail = ver[len(head):]
	return head, tail

# save incremental, preserves version formatting
def saveInc():
	hipname = hou.getenv('HIPNAME')
	if hipname != 'untitled':
		v, num = verSplit( hipname.split("_")[-1] )
		num = str( int(num) + 1 ).zfill( len(num) )
		newName = hipname.split("_")
		newName[-1] = v + num
		newNameStr = hou.getenv('HIP') + "/" + "_".join(newName) + "." + hou.getenv('HIPFILE').split(".")[-1]
		hou.hipFile.save(newNameStr)
		initVars()
	else:
		print "cannot increment version name in untitled.hip"

# loads back last crashed file
def crashRecovery():
	path = hou.getenv("HOUDINI_TEMP_DIR")
	os.chdir(path)
	files = [file for file in glob.glob("*.hip*")]
	if len(files) != 0:
		hou.hipFile.load( path + "/" + files[-1] )
	else:
		print "no crashed files found"

# flattens down list of lists
def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt

# return list of folders inside specified folder
def getFoldersPaths(path):
	folders = [x[0] for x in os.walk(path)]
	del folders[0]
	return folders

# return list of files matching mask inside specified folder
def getFilesByMask(path, mask):
	os.chdir(path)
	lods = [file for file in glob.glob(mask)]
	return lods

def batchRename(nodes):
	prefix = hou.ui.readInput("name prefix:", buttons=("rename",), title="rename nodes")[1]
	for i, node in enumerate(nodes):
		node.setName(prefix + str(i), unique_name=True)

class MegaLoad():
	'''
	class for handling Megascans assets
	'''
	megaPath = hou.getenv("MEGASCANS3D")
	megaHierarchyFile = megaPath + "index.json"

	with open(megaHierarchyFile) as data:
		assetsIndex = json.load(data)

	# writes dictionary with hierarchy of all megascan packs, assets their LODs
	def buildHierarchy(self):
		# returns True if asset and LOD are reversed
		def checkReverse(packs, pack):
			assetName = getFilesByMask(self.megaPath + packs[pack] + "/", "*.bgeo.sc")[0]
			assetName = assetName.split(".")[0].split("_")[-1]
			if assetName.isdigit():
				correct = False
			else:
				correct = True
			return correct

		# returns list of assets in a pack
		def getAssets(packs, pack):
			assets = getFilesByMask(self.megaPath + packs[pack] + "/", "*.bgeo.sc")
			if checkReverse(packs,  pack):
				assets = [ asset.split(".")[0].split("_")[-2] for asset in assets ]
			else:
				assets = [ asset.split(".")[0].split("_")[-1] for asset in assets ]
			assets = list(set(assets))
			return assets

		# returns dictionary of LODs per asset in pack as keys and full paths as values
		def getLods(packs, pack, assets, asset):
			lods = getFilesByMask(self.megaPath + packs[pack] + "/", "*" + assets[asset] + "*" + "*.bgeo.sc")
			if checkReverse(packs,  pack):
				lods = { lod.split(".")[0].split("_")[-1] : packs[pack] + "/" + lod for lod in lods }
			else:
				lods = { lod.split(".")[0].split("_")[-2] : packs[pack] + "/" + lod for lod in lods }
			return lods

		packs = getFoldersPaths(self.megaPath)
		packs = [x.split("/")[-1] for x in packs]

		hierarchy = {}
		for pack in xrange(len(packs)):
			assets = getAssets(packs, pack)
			assetDict = {}
			for asset in xrange(len(assets)):
				lods = getLods(packs, pack, assets, asset)
				assetDict[assets[asset]] = lods
			hierarchy[packs[pack]] = assetDict

		with open(self.megaHierarchyFile, 'w') as out:
			json.dump(hierarchy, out, indent = 1, sort_keys=True, ensure_ascii=False)

	# finds packs based on idexed file, outputs houdini menu-style list
	def packsList(self):
	 	packs = [pack.encode("ascii") for pack in self.assetsIndex]
		packs = [[packs[x], packs[x].replace("_", " ")] for x in xrange(len(packs))]
		packs = flatten(packs)
		return packs

	# finds assets in pack based on idexed file, outputs houdini menu-style list
	def assetsList(self):
		index = hou.pwd().parm("pack").eval()
		packs = hou.pwd().parm("pack").menuItems()
		pack = packs[index]

		assets = self.assetsIndex[pack].keys()
		assets = [x.encode("ascii") for x in assets]
		assets = [ [x,x] for x in assets]
		assets = flatten(assets)
		return assets

	# finds LODs in asset in pack based on idexed file, outputs houdini menu-style list
	def lodsList(self):
		packsIndex = hou.pwd().parm("pack").eval()
		packs = hou.pwd().parm("pack").menuItems()
		pack = packs[packsIndex]

		assetsIndex = hou.pwd().parm("asset").eval()
		assets = hou.pwd().parm("asset").menuItems()
		asset = assets[assetsIndex]

		lods = self.assetsIndex[pack][asset].keys()
		lods = [x.encode("ascii") for x in lods]
		paths = [self.assetsIndex[pack][asset][lod].encode("ascii") for lod in lods]
		lodsMenu = [ [ self.megaPath + paths[n] , lods[n] ] for n in xrange(len(lods))]
		lodsMenu = flatten(lodsMenu)
		return lodsMenu

	# checks checkbox in asset, if set, it will rename current node by asset name and LOD, it should be bound to callback of a load button (which might by hidden)
	def autoRename(self, node):
	    currentName = node.name()
	    enabled = node.evalParm("rename")
	    
	    packs = node.parm("pack").menuItems()
	    pack = node.parm("pack").eval()
	    assets = node.parm("asset").menuLabels()
	    asset = node.parm("asset").eval()
	    lods = node.parm("lod").menuLabels()
	    lod = node.parm("lod").eval()
	    
	    newName = packs[pack] + "_" + assets[asset] + "_" + lods[lod] + "_0"
	    
	    if enabled and (currentName != newName):
	        node.setName(newName, unique_name=True)

	# searches houdini project file for shaders which are prepared to work with megascans assets, if found, it modifies parameter values
	def getShaders(self, node):
	    restInstances = hou.nodeType(hou.shopNodeTypeCategory(), 'jt_megaShader').instances()
	    lod0Instances = hou.nodeType(hou.shopNodeTypeCategory(), 'jt_megaShader_lod0').instances()
	    
	    rest = "--- shader not found ---"
	    lod0 = "--- shader not found ---"
	    
	    if len(restInstances) != 0:
	        rest = restInstances[0].path()
	    if len(lod0Instances) != 0:
	        lod0 = lod0Instances[0].path()
	    
	    node.parm("rest").set(rest)
	    node.parm("lod0").set(lod0)