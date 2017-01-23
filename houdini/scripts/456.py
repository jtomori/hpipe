'''
houdini startup script
it imports hpipe module into houdini session
script expects $PIPELINE environment variable present in Houdini, set in houdini.env / batch script
'''
code = """# adds pipeline scripts into python path, imports hpipe module
import sys
path = hou.expandString("$PIPELINE") + "\python"
sys.path.append(path)
import hpipe

# initialize shot-based variables
hpipe.initVars()
"""
import time, hou
hou.setSessionModuleSource(code)