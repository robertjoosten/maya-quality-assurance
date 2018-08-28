from maya import cmds, OpenMaya, OpenMayaAnim
from ..utils import QualityAssurance, reference, skin, api


class UnusedInfluences(QualityAssurance):
    """
    Skin clusters will be checked to see if they contain unused influences.
    When fixing this error the unused influences will be removed from the skin
    cluster.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unused Influences"
        self._urgency = 1
        self._message = "{0} skin cluster(s) contain unused influences"
        self._categories = ["Skinning"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Skin clusters with unused influences
        :rtype: generator
        """
        skinClusters = self.ls(type="skinCluster")
        skinClusters = reference.removeReferenced(skinClusters)

        for skinCluster in skinClusters:
            mesh = cmds.skinCluster(skinCluster, query=True, geometry=True)
            if not mesh:
                continue
                
            weighted = cmds.skinCluster(
                skinCluster, 
                query=True, 
                weightedInfluence=True 
            )
            influences = cmds.skinCluster(
                skinCluster, 
                query=True, 
                influence=True
            )
            
            for i in influences:
                if i not in weighted:
                    yield skinCluster
                    break

    def _fix(self, skinCluster):
        """
        :param str skinCluster:
        """
        weighted = cmds.skinCluster(
                skinCluster, 
                query=True, 
                weightedInfluence=True 
        )
        
        influences = cmds.skinCluster(
            skinCluster, 
            query=True, 
            influence=True
        )
        
        for i in influences:
            if i not in weighted:
                cmds.skinCluster(skinCluster, edit=True, removeInfluence=i)

                
class MaximumInfluences(QualityAssurance):
    """
    Skin clusters will be checked to see if they contain vertices that exceed
    the maximum influences. When fixing this error new skin weights will be 
    applied by removing and normalizing the lowest influences that are 
    exceeding the maximum amount.
    cluster.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Maximum Influences"
        self._message = "{0} skin cluster(s) exceed the maximum influences"
        self._categories = ["Skinning"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Skin clusters which exceed maximum influences.
        :rtype: generator
        """
        # variables
        obj = OpenMaya.MObject()

        # get skin cluster iterator
        iterator = self.lsApi(nodeType=OpenMaya.MFn.kSkinClusterFilter)
        
        # iterate skin cluster
        while not iterator.isDone():
            # variables
            iterator.getDependNode(obj)
            depNode = OpenMaya.MFnDependencyNode(obj)
            skinFn = OpenMayaAnim.MFnSkinCluster(obj)
            skinCluster = depNode.name()
            
            # skin cluster data
            maintain = "{0}.maintainMaxInfluences".format(skinCluster)
            maintain = cmds.getAttr(maintain)
            maxInfluences = "{0}.maxInfluences".format(skinCluster)
            maxInfluences = cmds.getAttr(maxInfluences)

            # skip if max influences doesn't have to be maintained
            if not maintain:
                iterator.next()
                continue
            
            # get influences
            infIds, infPaths = skin.getInfluencesApi(skinFn)
            
            # get weights
            for weight in skin.getWeightsApiGenerator(skinFn, infIds):
                if len([w for w in weight.values() if w]) > maxInfluences:
                    yield skinCluster
                    break

            iterator.next()
     
    def _fix(self, skinCluster):
        """
        :param str skinCluster:
        """
        obj = api.toMObject(skinCluster)
        skinFn = OpenMayaAnim.MFnSkinCluster(obj)
        
        # normalize
        normalizePath = "{0}.normalizeWeights".format(skinCluster)
        normalize = cmds.getAttr(normalizePath)
         
        # max influence data
        maxInfluencesPath = "{0}.maxInfluences".format(skinCluster)
        maxInfluences = cmds.getAttr(maxInfluencesPath)
        
        # get influences
        infIds, infPaths = skin.getInfluencesApi(skinFn)
        infIdsLocked = {
            i: cmds.getAttr("{0}.liw".format(infPaths[i]))
            for _, i in infIds.iteritems()
        }
        
        # get weights
        weights = skin.getWeightsApi(skinFn, infIds)

        for vId, vWeights in weights.iteritems():
            # variable
            nWeights = vWeights.copy()
        
            # sort weights
            ordered = sorted(vWeights.items(), key=lambda x: -x[1])
        
            keepIndices = [
                index 
                for i, (index, weight) in enumerate(ordered) 
                if i <= maxInfluences-1
            ]
            removeIndices = [
                index 
                for i, (index, weight) in enumerate(ordered) 
                if i > maxInfluences-1
            ]
            
            # remove weights
            for i in removeIndices:
                nWeights[i] = 0
            
            # normalize weights
            if normalize == 1:
                # get normalizable weights
                normalizeIndices = [
                    i
                    for i in keepIndices
                    if not infIdsLocked.get(i)
                ]
                
                # if no weights can be normalized, normalize all
                if not normalizeIndices:
                    normalizeIndices = keepIndices
                
                # get normalizing multiplier
                total = sum([vWeights.get(i) for i in normalizeIndices])
                multiplier = 1/total
                
                # normalize indices
                for i in normalizeIndices:
                    nWeights[i] = vWeights.get(i) * multiplier       
            
            # set weights
            for infId, infValue in nWeights.items():
                infAttr = "{0}.weightList[{1}].weights[{2}]".format(
                    skinCluster,
                    vId,
                    infId
                )
                cmds.setAttr(infAttr, infValue)
