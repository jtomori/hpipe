import os
import nuke
import gizmos
import disconnect_wiggle
import plugin_nuke

# auto load all gizmos
gizmosPath = "//bigfoot/jellyfish/00_pipeline/nuke/gizmos"
nuke.pluginAddPath(gizmosPath)
menuNodes = nuke.menu( 'Nodes' )
gizmos.addGizmos(gizmosPath, menuNodes)

# load render threads
menuMain = nuke.menu( 'Nodes' ).menu("Jellyfish")
menuMain.addCommand("vuRenderThreads", "plugin_nuke.showPopup()", "Alt+F7")

# set up defaults
nuke.knobDefault("Root.format", "HD_1080")
nuke.knobDefault("Root.fps", os.environ['FPS'])

# set up favorites
jf = os.environ['ROOT'].replace("\\", "/")
nuke.addFavoriteDir('JELLYFISH', jf)
nuke.addFavoriteDir('JF USER', os.environ['HOME'])
nuke.addFavoriteDir('JF SHOTS', jf + '/30_shots')
nuke.addFavoriteDir('JF RENDER', jf + '/40_render')
nuke.addFavoriteDir('JF FOOTAGE', jf + '/45_footage')