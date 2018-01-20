from maya import cmds
from ..utils import QualityAssurance, reference


class DeleteNonDeformerHistory(QualityAssurance):
    """
    Meshes will be checked to see if they contain non-deformer history. Be
    carefull with this ceck as it is not always nessecary to fix this. History
    is not always a bad thing. When fixing this error the partial history will
    be baked.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Non Deformer History"
        self._message = "{0} mesh(es) contain non-deformer history nodes"
        self._categories = ["Rigging"]
        self._selectable = True

        self._ignoreNodeTypes = [
            "geometryFilter", "tweak", "groupParts",
            "groupId", "shape", "dagPose",
            "joint", "shadingEngine", "cluster",
            "transform", "diskCache", "time"
        ]

    # ------------------------------------------------------------------------

    @property
    def ignoreNodeTypes(self):
        return self._ignoreNodeTypes

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Meshes with non-deformer history
        :rtype: generator
        """
        meshes = self.ls(type="mesh")
        meshes = reference.removeReferenced(meshes)

        for mesh in meshes:
            history = cmds.listHistory(mesh)
            deformers = cmds.ls(history, type=self.ignoreNodeTypes)

            if len(history) != len(deformers):
                yield mesh

    def _fix(self, mesh):
        """
        :param str mesh:
        """
        cmds.bakePartialHistory(mesh, prePostDeformers=True)


class DeleteNonSetDrivenAnimation(QualityAssurance):
    """
    Animation curves will be checked to see if they are not set driven keys.
    Non set driven keys should not be present in the scene and will be deleted
    when fixing this error.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Non Set-Driven Animation"
        self._message = "{0} non set-driven animation curve(s) in the scene"
        self._categories = ["Rigging"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Non set driven key animation curves
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)

        for animCurve in animCurves:
            if not cmds.listConnections("{0}.input".format(animCurve)):
                yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        cmds.delete(animCurve)
