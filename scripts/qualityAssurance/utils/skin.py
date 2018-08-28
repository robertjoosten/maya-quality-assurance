from maya import cmds, OpenMaya, OpenMayaAnim


def getInfluencesApi(skinFn):
    """
    Get influence data from a skin cluster
    Code written by Tyler Thornock: http://www.charactersetup.com/home.html
    
    :param OpenMayaAnim.MFnSkinCluster skinFn:
    :return: Influences dictionary and list
    :rtype: tuple()
    """
    # get the MDagPath for all influence
    infDags = OpenMaya.MDagPathArray()
    skinFn.influenceObjects(infDags)
    
    # create dictionary with MDagPath
    # create list with full path of influences
    infIds = {}
    infPaths = []
    for x in xrange(infDags.length()):
        infPath = infDags[x].fullPathName()
        infId = int(skinFn.indexForInfluenceObject(infDags[x]))
        infIds[infId] = x
        infPaths.append(infPath)
        
    return infIds, infPaths
    
    
def getWeightsApiGenerator(skinFn, infIds):
    """
    Get skin weights from a skin cluster reading its attributes.
    Code written by Tyler Thornock: http://www.charactersetup.com/home.html
    
    :param OpenMayaAnim.MFnSkinCluster skinFn:
    :param dict infIds:
    :return: Skin weights per vertex
    :rtype: generator
    """
    wlPlug = skinFn.findPlug("weightList")
    wPlug = skinFn.findPlug("weights")
    wlAttr = wlPlug.attribute()
    wAttr = wPlug.attribute()
    wInfIds = OpenMaya.MIntArray()

    # the weights are stored in dictionary, the key is the vertId, 
    # the value is another dictionary whose key is the influence id and 
    # value is the weight for that influence
    for vId in xrange(wlPlug.numElements()):
        vWeights = {}
        # tell the weights attribute which vertex id it represents
        wPlug.selectAncestorLogicalIndex(vId, wlAttr)
        
        # get the indice of all non-zero weights for this vert
        wPlug.getExistingArrayAttributeIndices(wInfIds)

        # create a copy of the current wPlug
        infPlug = OpenMaya.MPlug(wPlug)
        for infId in wInfIds:
            # tell the infPlug it represents the current influence id
            infPlug.selectAncestorLogicalIndex(infId, wAttr)
            
            # add this influence and its weight to this verts weights
            try:
                vWeights[infIds[infId]] = infPlug.asDouble()
            except KeyError:
                # assumes a removed influence
                pass
                
        yield vWeights
    
    
def getWeightsApi(skinFn, infIds):
    """
    Get skin weights from a skin cluster reading its attributes.
    Code written by Tyler Thornock: http://www.charactersetup.com/home.html
    
    :param OpenMayaAnim.MFnSkinCluster skinFn:
    :param dict infIds:
    :return: Dictionary of skin weights.
    :rtype: dict
    """
    weights = {}
    
    wlPlug = skinFn.findPlug("weightList")
    wPlug = skinFn.findPlug("weights")
    wlAttr = wlPlug.attribute()
    wAttr = wPlug.attribute()
    wInfIds = OpenMaya.MIntArray()

    # the weights are stored in dictionary, the key is the vertId, 
    # the value is another dictionary whose key is the influence id and 
    # value is the weight for that influence
    for vId in xrange(wlPlug.numElements()):
        vWeights = {}
        # tell the weights attribute which vertex id it represents
        wPlug.selectAncestorLogicalIndex(vId, wlAttr)
        
        # get the indice of all non-zero weights for this vert
        wPlug.getExistingArrayAttributeIndices(wInfIds)

        # create a copy of the current wPlug
        infPlug = OpenMaya.MPlug(wPlug)
        for infId in wInfIds:
            # tell the infPlug it represents the current influence id
            infPlug.selectAncestorLogicalIndex(infId, wAttr)
            
            # add this influence and its weight to this verts weights
            try:
                vWeights[infIds[infId]] = infPlug.asDouble()
            except KeyError:
                # assumes a removed influence
                pass
                
        weights[vId] = vWeights
        
    return weights
