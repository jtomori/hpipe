'''
hpipe - collection of useful functions
base for houdini pipeline
created by Juraj Tomori
'''

import glob, os, json, subprocess
import hou
import toolutils as tu

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
	
# batch rename incoming nodes (from  selection) by specified prefix and selection order
def batchRename(nodes):
	prefix = hou.ui.readInput("name prefix:", buttons=("rename",), title="rename nodes")[1]
	if prefix != '':
		for i, node in enumerate(nodes):
			node.setName(prefix + str(i), unique_name=True)

# a tool for linking capture regions of multiple bone chains to the master one
def linkCaptures(nodes):
	if len(nodes) != 0:
		for node in nodes:
			i = node.name().split("_")[-1]
			expr = { 	'ccrtopcapx' : 'ch("../0_bone_' + i + '/ccrtopcapx")',
						'ccrtopcapy' : 'ch("../0_bone_' + i + '/ccrtopcapy")',
						'ccrtopcapz' : 'ch("../0_bone_' + i + '/ccrtopcapz")',
						'ccrbotcapx' : 'ch("../0_bone_' + i + '/ccrbotcapx")',
						'ccrbotcapy' : 'ch("../0_bone_' + i + '/ccrbotcapy")',
						'ccrbotcapz' : 'ch("../0_bone_' + i + '/ccrbotcapz")'
					}
			node.setParmExpressions(expr)

# tool for quick and easy creating of viewport flipbooks, to be implemented later.., watermark can be done maybe with hwatermark or something, settings does not have an option for that
def flipBooker():
	viewer = tu.sceneViewer()
	settings = viewer.flipbookSettings().stash()

	path = hou.getenv("HIP") + "/prev/" + hou.getenv("VER") + "/"
	if not os.path.isdir(path):
		os.makedirs(path)
	path = path + "out_$F4.jpg"
	settings.output(path)

	viewer.flipbook(settings=settings)

# class for custom Royal Renderfarm submitter
# reload(hou.session.hpipe); rr = hou.session.hpipe.RR(); rr.renderIfdSubmit()
class RR():
	# init default variables
	def __init__(self):
		self.rr_root = os.environ['RR_ROOT'] + "\\bin\\win64\\"
		self.rr_file = hou.hipFile.path()
		self.rr_env = 'OverrideRREnvFile=1~<CompanyProjectRootFolder>00_pipeline\\houdini\\renderfarm.rrEnv'
		self.rr_ui = ["", ""]
		self.rr_ui = ['UIStyle=1~violaUI', "-violaUI"]

	# construct command for submitting to RR
	def submitToRR(self, file=None, env=None, mem=4, priority=50, maxClients=500, ui=None, rrSubmitter=False, dry=False, log=False):
		quot = "\""
		params = []
		
		# assign defaults if not specified
		if file == None:
			file = self.rr_file
		if env == None:
			env = self.rr_env
		if ui == None:
			ui = self.rr_ui
		
		params.append(quot + file + quot)
		params.append(quot + env + quot)
		params.append(quot + '-Software Houdini' + quot)
		params.append(quot + 'RenderPreviewFirst=1~0' + quot)
		params.append(quot + 'PPCreateSmallVideo=1~0' + quot)
		params.append(quot + 'PPSequenceCheck=1~0' + quot)
		params.append(quot + 'RequiredMemory=1~' + str(mem) + quot)
		params.append(quot + 'Priority=1~' + str(priority) + quot)
		params.append(quot + 'MaxClientsAtATime=1~' + str(maxClients) + quot)
		#params.append(quot + 'Layer=/out/mantra3' + quot) ---- not picking
		#params.append(quot + 'SequenceDivide=1~1' + quot) ---- not having an effect in UI
		if ui != ["", ""]:
			params.append(quot + ui[0] + quot)
		# add only if called from python, do not append in case of hscript (different out format)
		if log:
			params.append(" >> //bigfoot/jellyfish/00_pipeline/houdini/renderfarm.log")
		
		# flatten parameters
		params = " ".join(params)

		# submit
		if not rrSubmitter:
			cmd = self.rr_root + "rrSubmitterconsole.exe " + params
		else:
			cmd = self.rr_root + "rrSubmitter.exe " + params
		
		if not dry:
			#subprocess.Popen(cmd)
			os.system(cmd)
		
		# debug
		print "command to sent to RR: "
		print cmd + "\n"

		return cmd

	# generate IFDs and sent to RR
	def renderIfdSubmit(self, me, background=True, rrControl=True):
		# get input nodes
		nodes = me.inputAncestors()
		paths = []

		# get parameters from the node
		mem = me.evalParm("mem")
		priority = me.evalParm("priority")
		maxClients = me.evalParm("maxClients")
		rrSubmitter = me.evalParm("rrSubmitter")
		dry = me.evalParm("dry")

		# keep only mantra nodes
		nodesNew = []
		for node in nodes:
			if node.type() == hou.nodeType(hou.ropNodeTypeCategory(), "ifd"):
				nodesNew.append(node)
		nodes = nodesNew

		# enable IFD saving parameter, derive ifd path from image path and save path to list
		for node in nodes:
			pathImg = node.parm("vm_picture").unexpandedString()
			pathImg = pathImg.split("/")
			pathImg.insert(len(pathImg)-1, "ifd")
			pathImg = "/".join(pathImg)
			pathImg = pathImg.split(".")
			pathImg[-1] = "ifd"
			pathImg = ".".join(pathImg)
			node.parm("soho_diskfile").set(pathImg)
			node.parm("soho_outputmode").set(1)
			firstFrame = node.evalParm("f1")
			pathCurrent = node.parm("soho_diskfile").evalAtFrame(firstFrame)
			paths.append(pathCurrent)
			# enable and set post render script
			if background:
				script = self.submitToRR(file=pathCurrent, mem=mem, priority=priority, maxClients=maxClients, rrSubmitter=False, dry=True)
				script = "unix \'" + script.replace("\\", "/") + " >>& //bigfoot/jellyfish/00_pipeline/houdini/renderfarm.log\'"
				node.setParms({"tpostrender": 1, "lpostrender": "hscript", "postrender": script})

		# execute in background / normal
		if not dry:
			if background:
				hou.hipFile.save()
				for node in nodes:
					node.parm("executebackground").pressButton()
			else:
				for node in nodes:
					node.render()
		
		# disable IFD generation parameter and send to RR if not background
		for i, node in enumerate(nodes):
			node.parm("soho_outputmode").set(0)
			if not background:
				self.submitToRR(file=paths[i], mem=mem, priority=priority, maxClients=maxClients, rrSubmitter=rrSubmitter, dry=dry, log=True)
			else:
				node.setParms({"tpostrender": 0})

		# run rrControl
		if rrControl:
			subprocess.Popen(self.rr_root + "rrControl.exe " + self.rr_ui[1])

# class for handling Megascans assets
class MegaLoad():
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