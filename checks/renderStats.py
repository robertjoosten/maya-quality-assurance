from maya import cmds
from ..utils import QualityAssurance


class PrimaryVisibility(QualityAssurance):
    """
    Meshes will be checked to see if the primary visibility is on. When
    fixing this error the primary visibility will be turned on.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Primary Visibility"
        self._message = "{0} mesh(es) are not visible"
        self._categories = ["Render Stats"]
        self._selectable = True

        self._attribute = ".primaryVisibility"
        self._errorBool = False

    # ------------------------------------------------------------------------

    @property
    def attribute(self):
        return self._attribute

    @property
    def errorBool(self):
        return self._errorBool

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Find meshes that have the attribute set to the error boolean
        :rtype: generator
        """
        meshes = self.ls(type="mesh")

        for mesh in meshes:
            if cmds.getAttr(mesh + self.attribute) == self.errorBool:
                yield mesh

    def _fix(self, mesh):
        """
        :param str mesh:
        """
        cmds.setAttr(mesh + self.attribute, not self.errorBool)


class VisibleInRefraction(PrimaryVisibility):
    """
    Meshes will be checked to see if they are visible in refraction. When
    fixing this error the visible in refraction will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Visible in Refraction"
        self._message = "{0} mesh(es) are not visible in refraction"

        self._attribute = ".visibleInRefractions"
        self._errorBool = False


class VisibleInReflection(PrimaryVisibility):
    """
    Meshes will be checked to see if they are visible in reflection. When
    fixing this error the visible in reflection will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Visible in Reflection"
        self._message = "{0} mesh(es) are not visible in reflection"

        self._attribute = ".visibleInReflections"
        self._errorBool = False


class CastShadows(PrimaryVisibility):
    """
    Meshes will be checked to see if they cast shadows. When fixing this
    error the casting of shadows will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Cast Shadows"
        self._message = "{0} mesh(es) don't cast shadows"

        self._attribute = ".castsShadows"
        self._errorBool = False


class ReceiveShadows(PrimaryVisibility):
    """
    Meshes will be checked to see if they receive shadows. When fixing this
    error the receiving of shadows will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Receive Shadows"
        self._message = "{0} mesh(es) don't receive shadows"

        self._attribute = ".receiveShadows"
        self._errorBool = False


class SmoothShading(PrimaryVisibility):
    """
    Meshes will be checked to see if they are smooth shaded. When fixing this
    error the smooth shading will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Smooth Shading"
        self._message = "{0} mesh(es) are not smooth shaded"

        self._attribute = ".smoothShading"
        self._errorBool = False


class DoubleSided(PrimaryVisibility):
    """
    Meshes will be checked to see if they are double sided. When fixing this
    error double sided will be turned on.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Double Sided"
        self._message = "{0} mesh(es) are not double sided"

        self._attribute = ".doubleSided"
        self._errorBool = False


class Opposite(PrimaryVisibility):
    """
    Meshes will be checked to see if they are set to opposite. When fixing
    this error opposite state will be turned off.
    """
    def __init__(self):
        PrimaryVisibility.__init__(self)

        self._name = "Opposite"
        self._message = "{0} mesh(es) are set to opposite"

        self._attribute = ".opposite"
        self._errorBool = True
