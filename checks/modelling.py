from maya import cmds
from ..utils import QualityAssurance, reference


class FreezeTransforms(QualityAssurance):
    """
    Transforms will be checked to see if they have unfrozen attributes When
    fixing this error transforms will be frozen.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Freeze Transforms"
        self._message = "{0} transform(s) are not frozen"
        self._categories = ["Modelling"]
        self._selectable = True

        self._ignoreNodes = ["|persp", "|front", "|top", "|side"]

        self._attributes = [
            ".tx", "ty", "tz",
            ".rx", "ry", "rz",
            ".sx", "sy", "sz"
        ]
        self._values = [
            0, 0, 0,
            0, 0, 0,
            1, 1, 1
        ]

    # ------------------------------------------------------------------------

    @property
    def ignoreNodes(self):
        """
        :return: Nodes to ignore
        :rtype: list
        """
        return self._ignoreNodes

    @property
    def defaultState(self):
        """
        :return: Default state of attributes with values
        :rtype: list
        """
        return zip(self._attributes, self._values)

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Unfrozen transforms
        :rtype: generator
        """
        transforms = self.ls(transforms=True, l=True)
        transforms = reference.removeReferenced(transforms)

        for transform in transforms:
            if transform in self.ignoreNodes:
                continue

            for attr, value in self.defaultState:
                if not cmds.objExists(transform + attr):
                    continue

                if cmds.getAttr(transform + attr) != value:
                    yield transform

    def _fix(self, transform):
        """
        :param str transform:
        """
        cmds.makeIdentity(
            transform,
            apply=True,
            translate=True,
            rotate=True,
            scale=True
        )


class DeleteHistory(QualityAssurance):
    """
    Mesh shapes will be checked to see if they have history attached to them.
    When fixing this error the history will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "History"
        self._message = "{0} mesh(es) contain history nodes"
        self._categories = ["Modelling"]
        self._selectable = True

        self._ignoreNodes = [
            "tweak", "groupParts", "groupId",
            "shape", "shadingEngine", "mesh"
        ]


    # ------------------------------------------------------------------------

    @property
    def ignoreNodes(self):
        """
        :return: Nodes to ignore
        :rtype: list
        """
        return self._ignoreNodes

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Meshes with history
        :rtype: generator
        """

        meshes = self.ls(type="mesh", l=True)
        meshes = reference.removeReferenced(meshes)

        for mesh in meshes:
            history = cmds.listHistory(mesh) or []
            types = [cmds.nodeType(h) for h in history]

            for t in types:
                if t in self.ignoreNodes:
                    continue

                yield mesh
                break

    def _fix(self, mesh):
        """
        :param str mesh:
        """
        cmds.delete(mesh, ch=True)


class DeleteAnimation(QualityAssurance):
    """
    All animation curves will be added to the error list. When fixing this
    error the animation curves will be deleted
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Animation"
        self._message = "{0} animation curve(s) in the scene"
        self._categories = ["Modelling"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves
        :rtype: generator
        """

        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)

        for animCurve in animCurves:
            yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        cmds.delete(animCurve)
