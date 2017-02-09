import nuke

# Settings
wiggle_number = 4
wiggle_treshold = 15

# Global variables
wig_prevNode = None
wig_origX = None
wig_prevXhit = None
wig_hitCount = 0

def wiggle():
    try:
        node = nuke.thisNode()
        knob = nuke.thisKnob()
        global wig_prevNode
        global wig_origX
        global wig_prevXhit
        global wig_hitCount
        
        if node.name() != wig_prevNode: # If we we select a new node, reset the number of wiggles
            wig_prevNode = node.name()
            wig_origX = node.knob("xpos").value()
            wig_prevXhit = None
            wig_hitCount = 0
        
        elif knob.name() == 'xpos': # We only need to check the wiggle if we're moving the node in X
            if wig_hitCount >= wiggle_number: # if we already hit the right number of wiggles, we extract the node
                nodeChildren = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                nodeParent = node.input(0)
                # Disconnect
                nuke.Undo().enable()
                nuke.Undo().name('wiggle extract')
                for i in range(node.inputs()):
                    node.setInput(i, None)
                # Connect Children
                for n in nodeChildren:
                    for ic in range(n.inputs()):
                        if n.input(ic) == node:
                            n.setInput(ic, nodeParent)
                            break
                # reset the number of wiggles
                wig_hitCount = 0
                #nuke.Undo().new()
                nuke.Undo().disable()
                return
            
            else: # if we didn't wiggle enough, check by how much we moved the node
                value = knob.value()
                distance = value-wig_origX
                if abs(distance) > wiggle_treshold:
                    if wig_hitCount == 0:
                        wig_hitCount += 1
                        wig_prevXhit = distance
                    elif wig_prevXhit > 0 and distance < 0:
                        wig_hitCount += 1
                        wig_prevXhit = distance
                    elif wig_prevXhit < 0 and distance > 0:
                        wig_hitCount += 1
                        wig_prevXhit = distance
    except:
        return

nuke.addKnobChanged(wiggle)
