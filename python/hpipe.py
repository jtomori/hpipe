'''
hpipe - collection of useful functions
base for houdini pipeline
created by Juraj Tomori
'''

import glob, os
import hou
from itertools import cycle
import numpy as np

# shot name template: s010_shotName_fx_cloudSetup_v001.hipnc
# asset name template: fx_cloudRig_v001.hipnc
# initializes global variables in houdini session
def initVars():
	hipname = hou.getenv('HIPNAME')
	if hipname != 'untitled':
		attribs = hipname.split("_")
		if len(attribs) == 5:
			hou.putenv('SHOT', attribs[0])
			hou.putenv('SHOTNAME', attribs[1])
			hou.putenv('TASK', attribs[2])
			hou.putenv('TASKNAME', attribs[3])
			hou.putenv('VER', attribs[4])
		elif len(attribs) == 3:
			hou.putenv('TASK', attribs[0])
			hou.putenv('ASSET', attribs[1])
			hou.putenv('VER', attribs[2])

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

# function for histogram digital asset
def hist(node):
    geo = node.geometry()
    attrib = node.parm("attrib").eval()
    res = node.parm("res").eval() + 1
    norm = node.parm("norm").eval()
    vec = node.parm("vec").eval()
    precision = 1000000
    entity = node.parm("entity").eval()
        
    # get list of attribute values and convert to numpy array
    if entity == 0:
        vals = geo.pointFloatAttribValues(attrib)
    elif entity == 1:
        vals = geo.primFloatAttribValues(attrib)
    else:
        myPath = node.path()
        if not vec:
            volumePrimId = hou.hscriptExpression('listbyvals("' + myPath + '", D_PRIMITIVE, "name", ' + attrib + ')')
            volume = geo.prims()[int(volumePrimId)]
            vals = volume.allVoxels()
        else:
            attribVec = attrib + '.x'
            volumePrimIdX = hou.hscriptExpression('listbyvals("' + myPath + '", D_PRIMITIVE, "name", ' + attribVec + ')')
            volumeX = geo.prims()[int(volumePrimIdX)]
            attribVec = attrib + '.y'
            volumePrimIdY = hou.hscriptExpression('listbyvals("' + myPath + '", D_PRIMITIVE, "name", ' + attribVec + ')')
            volumeY = geo.prims()[int(volumePrimIdY)]
            attribVec = attrib + '.z'
            volumePrimIdZ = hou.hscriptExpression('listbyvals("' + myPath + '", D_PRIMITIVE, "name", ' + attribVec + ')')
            volumeZ = geo.prims()[int(volumePrimIdZ)]
            valsX = volumeX.allVoxels()
            valsY = volumeY.allVoxels()
            valsZ = volumeZ.allVoxels()
            iters = [iter(valsX), iter(valsY), iter(valsZ)]
            vals = list(it.next() for it in cycle(iters))
            
    if vec:
        vals = list(vals)
        vals = [vals[x:x+3] for x in xrange(0, len(vals), 3)]
        valsLength = []
        for i in vals:
            valsLength.append( np.linalg.norm(i) )
        vals = valsLength
    valsNp = np.asarray(vals)
    valsNp = np.round(valsNp, decimals=int(np.log10(precision)))
    
    # compute stats
    min = np.amin(valsNp)
    max = np.amax(valsNp)
    avg = np.average(valsNp)
    median = np.median(valsNp)
    
    # print to parameters
    node.parm("stats1").set(min)
    node.parm("stats2").set(max)
    node.parm("stats3").set(avg)
    node.parm("stats4").set(median)
    
    # compute, draw histogram
    valsHistNp = np.histogram(valsNp, bins=res, density=True)[0]
    
    valsHistNpMax = np.amax(valsHistNp)
    if norm:
        valsHistNp /= valsHistNpMax
    valsHist = tuple(valsHistNp)
    valsHist = tuple([ float(int(valsHist[i]*precision)) / precision for i in xrange(len(valsHist))])
    
    keysHist = tuple(np.linspace(0,1,res))
    keysHist = tuple([ float(int(keysHist[i]*precision)) / precision for i in xrange(len(keysHist))])

    basis = hou.rampBasis.Constant
    histRamp = hou.Ramp( (basis, basis), keysHist, valsHist )    
    node.parm("hist").set(histRamp)

class MegaLoad():
	'''
	class for handling Megascans assets
	'''

	# list available assets in megascans library, returns list formatted for houdini ordered menu, expects environment variable for path
	@staticmethod
	def megaAssetsList():
	    megaPath = hou.getenv("MEGASCANS") + '3d/'
	    assetsPaths = [x[0] for x in os.walk(megaPath)]
	    del assetsPaths[0]
	    assets = [x.split("/")[-1] for x in assetsPaths]        
	    assetsList = [[assetsPaths[x], assets[x].replace("_", " ")] for x in xrange(len(assets))]
	    assetsList = flatten(assetsList)

	    return assetsList

	# list available LODs in megascans library, it checks menu selection and scans respective directory for available LODs, returns asset path and name
	@staticmethod
	def megaAssetsLodList():
	    index = hou.pwd().parm("asset").eval()
	    paths = hou.pwd().parm("asset").menuItems()
	    path = paths[index]
	    
	    os.chdir(path)
	    lods = [file for file in glob.glob("*.obj")]
	    lods = [ [path + "/" + x, (x.split(".")[-2]).split("_")[-1]] for x in lods]
	    lods = flatten(lods)

	    return lods

	# checks checkbox in asset, if set, it will rename current node by asset name and LOD, it should be bound to callback of a load button (which might by hidden)
	@staticmethod
	def autoRename(node):
	    currentName = node.name()
	    enabled = node.evalParm("rename")
	    
	    labels = hou.pwd().parm("asset").menuLabels()
	    index = hou.pwd().parm("asset").eval()
	    
	    lods = hou.pwd().parm("lod").menuLabels()
	    lod = hou.pwd().parm("lod").eval()
	    
	    newName = labels[index]
	    newName = newName.replace(" ","_") + "_" + lods[lod] + "_0"
	    
	    if enabled and (currentName != newName):
	        node.setName(newName, unique_name=True)

	# searches houdini project file for shaders which are prepared to work with megascans assets, if found, it modifies parameter values
	@staticmethod	        
	def getShaders(node):
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

	@staticmethod
	def testMethod(str):
		print str