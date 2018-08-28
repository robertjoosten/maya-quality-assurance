import os
from maya import cmds
from ..utils import QualityAssurance, reference


class NonExistingTextures(QualityAssurance):
    """
    Animation curves will be checked to see if they are not set driven keys.
    Non set driven keys should not be present in the scene and will be deleted
    when fixing this error.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Non Existing Textures"
        self._message = "{0} file(s) contain a link to a not existing texture"
        self._categories = ["Textures"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Meshes with non-deformer history
        :rtype: generator
        """
        fileNodes = self.ls(type="file")
        for fileNode in fileNodes:
            path = cmds.getAttr("{0}.fileTextureName".format(fileNode))
            if not os.path.exists(path):
                yield fileNode

    def _fix(self, fileNode):
        """
        :param str fileNode:
        """
        cmds.setAttr("{0}.disableFileLoad".format(fileNode), 1)
