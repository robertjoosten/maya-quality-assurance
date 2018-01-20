from maya import cmds
from ..utils import QualityAssurance, reference


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
