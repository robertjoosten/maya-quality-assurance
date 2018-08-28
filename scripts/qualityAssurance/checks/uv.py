from maya import cmds
from ..utils import QualityAssurance, reference


class EmptyUVSets(QualityAssurance):
    """
    Meshes will be checked to see if they have empty uv sets. When fixing the
    uv set will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Empty UV Sets"
        self._message = "{0} empty uv set(s)"
        self._categories = ["UV"]
        self._selectable = False

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty UV Sets
        :rtype: generator
        """
        meshes = cmds.ls(type="mesh", noIntermediate=True, l=True)
        meshes = reference.removeReferenced(meshes)

        for mesh in meshes:
            uvSets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
            uvSetsIndex = cmds.polyUVSet(mesh, query=True, allUVSetsIndices=True)

            for uvSet, index in zip(uvSets, uvSetsIndex):
                if index == 0:
                    continue

                if not cmds.polyEvaluate(mesh, uvcoord=True, uvSetName=uvSet):
                    yield "{0}.uvSet[{1}].uvSetName".format(mesh, index)

    def _fix(self, meshAttribute):
        """
        :param str meshAttribute:
        """
        mesh = meshAttribute.split(".")[0]
        uvSet = cmds.getAttr(meshAttribute)

        cmds.polyUVSet(mesh, edit=True, delete=True, uvSet=uvSet)


class UnusedUVSets(QualityAssurance):
    """
    Meshes will be checked to see if they have unused uv sets. When fixing the
    uv set will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unused UV Sets"
        self._message = "{0} unused uv set(s)"
        self._categories = ["UV"]
        self._selectable = False

        self._ignoreUvSets = [
            "hairUVSet",
        ]

    # ------------------------------------------------------------------------

    @property
    def ignoreUvSets(self):
        return self._ignoreUvSets

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty UV Sets
        :rtype: generator
        """
        meshes = cmds.ls(type="mesh", noIntermediate=True, l=True)
        meshes = reference.removeReferenced(meshes)

        for mesh in meshes:
            uvSets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
            uvSetsIndex = cmds.polyUVSet(mesh, query=True, allUVSetsIndices=True)

            for uvSet, index in zip(uvSets, uvSetsIndex):
                if index == 0 or uvSet in self.ignoreUvSets:
                    continue

                attr = "{0}.uvSet[{1}].uvSetName".format(mesh, index)
                if not cmds.listConnections(attr):
                    yield attr

    def _fix(self, meshAttribute):
        """
        :param str meshAttribute:
        """
        mesh = meshAttribute.split(".")[0]
        uvSet = cmds.getAttr(meshAttribute)

        cmds.polyUVSet(mesh, edit=True, delete=True, uvSet=uvSet)
