from maya import cmds
from ..utils import QualityAssurance, reference


class NoShadingGroup(QualityAssurance):
    """
    Meshes will be checked to see if they have a shading group attached.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "No Shading Group Assignment"
        self._message = "{0} mesh(es) are not connected to any shading group"
        self._categories = ["Shaders"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Meshes without shading group attachment
        :rtype: generator
        """
        meshes = self.ls(type="mesh", noIntermediate=True, l=True)
        meshes = reference.removeReferenced(meshes)

        for mesh in meshes:
            shadingGroups = cmds.listConnections(mesh, type="shadingEngine")
            if not shadingGroups:
                yield mesh


class InitialShadingGroup(QualityAssurance):
    """
    Meshes will be checked to see if they have the default shading group
    attached.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Initial Shading Group Assignment"
        self._message = "{0} object(s) are connected to the initial shading group"
        self._categories = ["Shaders"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Meshes without shading group attachment
        :rtype: generator
        """
        shadingGroups = cmds.ls(type="shadingEngine")

        if "initialShadingGroup" not in shadingGroups:
            return

        connections = cmds.sets("initialShadingGroup", query=True) or []
        if not connections:
            return

        connections = cmds.ls(connections, l=True)
        for connection in connections:
            yield connection


class FaceAssignedShading(QualityAssurance):
    """
    Shading groups will be checked to see if they contain component
    connections. When fixing it will force a shape connections. If you
    intentially have component assigment, it is best to skip this check.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Face Assignment"
        self._urgency = 1
        self._message = "{0} shading group(s) contain a component connection"
        self._categories = ["Shaders"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty UV Sets
        :rtype: generator
        """
        shadingGroups = self.ls(type="shadingEngine")

        for shadingGroup in shadingGroups:
            connections = cmds.sets(shadingGroup, query=True) or []
            components = [
                connection.split(".")[0]
                for connection in connections
                if connection.count(".")
            ]

            if components:
                yield shadingGroup

    def _fix(self, shadingGroup):
        """
        :param str node:
        """
        connections = cmds.sets(shadingGroup, query=True) or []
        components = [
            connection
            for connection in connections
            if connection.count(".")
        ]

        if not components:
            return

        overview = dict()
        components = cmds.ls(components, fl=True, l=True)

        # collect faces per object
        for face in components:
            obj = face.split(".")[0]
            if cmds.nodeType(obj) == "transform":
                shape = cmds.listRelatives(obj, s=True, ni=True, f=True)[0]
            else:
                shape = obj[:]

            if not shape in overview.keys():
                overview[shape] = []

            overview[shape].append(face)

        # loop overview
        for shape, remove in overview.iteritems():
            if len(remove) != cmds.polyEvaluate(shape, face=True):
                raise RuntimeError("Incomplete Face Assigment")

            cmds.sets(remove, edit=True, remove=shadingGroup)
            cmds.sets(shape, edit=True, forceElement=shadingGroup)
