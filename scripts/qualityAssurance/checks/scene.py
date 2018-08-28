import re
import string
from maya import cmds, OpenMaya
from ..utils import QualityAssurance, reference, path


class DefaultName(QualityAssurance):
    """
    All transforms will be checked ti see if they start with a string that is
    considered to be a default name.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Default Names"
        self._urgency = 1
        self._message = "{0} transform(s) have a default name"
        self._categories = ["Scene"]
        self._selectable = True

        default = [
            "set", "locator", "imagePlane", "plane", "Text",
            "distanceDimension", "locator", "curve", "camera",
            "volumeLight", "areaLight", "spotLight", "pointLight",
            "directionalLight", "ambientLight", "pSolid", "pHelix",
            "nurbsSquare", "nurbsCircle", "cone", "box", "sphere",
            "group", "nurbsTorus", "nurbsPlane", "nurbsCone", "nurbsCylinder",
            "nurbsCube", "nurbsSphere", "pPipe", "pPyramid", "pTorus",
            "pPlane", "pCone", "pCylinder", "pCube", "pSphere", "null",
            "Char"
        ]

        self._regex = re.compile(
            "".join(["^(?:", "|".join(default), ")"])
        )

    # ------------------------------------------------------------------------

    @property
    def regex(self):
        """
        :return: Regex to find default names
        :rtype: _sre.SRE_Pattern
        """
        return self._regex

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Transforms that start with a default name
        :rtype: generator
        """
        transforms = self.ls(transforms=True)
        transforms = reference.removeReferenced(transforms)

        for transform in transforms:
            match = self.regex.match(transform)
            if not match:
                continue

            # yield error
            yield transform


class NamingConvention(QualityAssurance):
    """
    All nodes part of the predefined node type list are being checked to see
    if they follow the lower case split with a "_" naming convention. When
    fixing the error nodes will be renamed to follow the correct naming
    convention.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Naming Convention"
        self._urgency = 1
        self._message = "{0} node(s) don't follow the naming convention"
        self._categories = ["Scene"]
        self._selectable = True

        self._nodeTypes = ["transform", "joint"]

    # ------------------------------------------------------------------------

    @property
    def nodeTypes(self):
        """
        :return: List of node types that should be checked
        :rtype: list
        """
        return self._nodeTypes

    # ------------------------------------------------------------------------

    def splitOnCamelCase(self, n):
        """
        :param str n:
        :return: If n is upper case
        :rtype: bool
        """
        if n in string.ascii_uppercase:
            return True

    def splitOnDigit(self, n):
        """
        :param str n:
        :return: If n is a digit
        :rtype: bool
        """
        if n.isdigit():
            return True

    def splitOn(self, split, func):
        """
        :param list split: List of strings to split
        :param func: Function to split string by
        :return: Split sections
        :rtype: list
        """
        sections = []
        for s in split:
            splitIndices = [
                i for i, n in enumerate(s) if func(n)
            ]
            splitIndices = [
                i for i in splitIndices if not (i-1 in splitIndices)
            ]

            if 0 not in splitIndices and splitIndices:
                splitIndices.insert(0, 0)

            if not splitIndices:
                sections.append(s)
                continue

            splitIndices.append(-1)
            for i in range(len(splitIndices) - 1):
                if splitIndices[i+1] == -1:
                    sections.append(s[splitIndices[i]:])
                else:
                    sections.append(s[splitIndices[i]:splitIndices[i+1]])

        return sections

    # ------------------------------------------------------------------------

    def convertToNamingConvention(self, name):
        """
        Convert string to naming convention.

        :param str name:
        :return: Name adjusted to naming convention
        :rtype: str
        """
        # split namespace
        name = path.baseName(name)

        # split into sections
        sections = name.split("_")
        sections = [s[0].upper() + s[1:] for s in sections if s]

        sections = self.splitOn(sections, self.splitOnCamelCase)
        sections = self.splitOn(sections, self.splitOnDigit)

        # add delete on publish
        sections = [s.lower() for s in sections]

        return "_".join(sections)

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Nodes with incorrect naming convention
        :rtype: generator
        """
        nodes = self.ls(type=self.nodeTypes, l=True)
        nodes = reference.removeReferenced(nodes)
        nodes = sorted(nodes, key=lambda x: -len(x.split("|")))

        for node in nodes:
            if path.baseName(node) == self.convertToNamingConvention(node):
                continue

            # yield error
            yield node

    def _fix(self, node):
        """
        :param str node:
        """
        cmds.rename(node, self.convertToNamingConvention(node))


class UniqueName(QualityAssurance):
    """
    All transforms will be checked to see if their name is unique. When fixing
    the not uniquely named transforms will be made unique.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unique Names"
        self._message = "{0} transform(s) don't have a unique name"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Nodes with not unique naming
        :rtype: generator
        """
        obj = OpenMaya.MObject()
        iterator = self.lsApi(nodeType=OpenMaya.MFn.kTransform)
        while not iterator.isDone():
            iterator.getDependNode(obj)

            dagNode = OpenMaya.MDagPath.getAPathTo(obj)
            depNode = OpenMaya.MFnDependencyNode(obj)

            if not depNode.hasUniqueName():
                yield dagNode.fullPathName()

            iterator.next()

    def _fix(self, node):
        """
        :param str node:
        """
        # get root name
        root = path.rootName(node)

        # find new name
        for i in range(1, 1000):
            new = "{0}_{1:03d}".format(root, i)
            if not cmds.ls(new):
                break

        # rename node
        cmds.rename(node, new)


class UnknownNodes(QualityAssurance):
    """
    All unknown nodes will be added to the error list. When fixing these nodes
    will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unknown Nodes"
        self._message = "{0} unknown node(s)"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Unknown nodes
        :rtype: generator
        """
        unknownNodes = self.ls(type="unknown")
        unknownNodes = reference.removeReferenced(unknownNodes)

        for unknownNode in unknownNodes:
            yield unknownNode

    def _fix(self, node):
        """
        :param str node:
        """
        if cmds.lockNode(node, query=True, lock=True)[0]:
            cmds.lockNode(node, lock=False)

        cmds.delete(node)


class NotConnectedIntermediateShape(QualityAssurance):
    """
    All not connected intermediate nodes will be added to the error list.
    When fixing these nodes will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Not Connected Intermediate Shape"
        self._message = "{0} intermediate shape(s) are not connected"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Not connected intermediate nodes
        :rtype: generator
        """
        intermediates = self.ls(shapes=True, intermediateObjects=True)
        intermediates = reference.removeReferenced(intermediates)

        for intermediate in intermediates:
            if cmds.listConnections(intermediate):
                continue

            yield intermediate

    def _fix(self, intermediate):
        """
        :param str intermediate:
        """
        cmds.delete(intermediate)


class NotConnectedGroupID(QualityAssurance):
    """
    All not connected intermediate nodes will be added to the error list.
    When fixing these nodes will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Not Connected Group ID"
        self._message = "{0} group id(s) are not connected"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Not connected intermediate nodes
        :rtype: generator
        """
        groupIds = self.ls(type="groupId")
        groupIds = reference.removeReferenced(groupIds)

        for groupId in groupIds:
            if cmds.listConnections(groupId):
                continue

            yield groupId

    def _fix(self, groupId):
        """
        :param str groupId:
        """
        cmds.delete(groupId)


class HyperBookmarks(QualityAssurance):
    """
    All hyper bookmarks of the predefined node types will be added to the
    error list. When fixing these nodes will be deleted. To make sure no
    no connected nodes are deleted. The nodes will be locked before deletion.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Hyper Bookmarks"
        self._message = "{0} hyper bookmark(s) found"
        self._categories = ["Scene"]
        self._selectable = True

        self._nodeTypes = ["hyperLayout", "hyperGraphInfo", "hyperView"]
        self._nodeIgnore = ["hyperGraphInfo", "hyperGraphLayout"]

    # ------------------------------------------------------------------------

    @property
    def nodeTypes(self):
        """
        :return: List of node types that should be checked
        :rtype: list
        """
        return self._nodeTypes

    @property
    def nodeIgnore(self):
        """
        :return: List of nodes to be ignored
        :rtype: list
        """
        return self._nodeIgnore

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Hyper book marks
        :rtype: generator
        """
        bookmarks = self.ls(type=self.nodeTypes)
        bookmarks = reference.removeReferenced(bookmarks)

        for bookmark in bookmarks:
            if bookmark in self.nodeIgnore:
                continue

            yield bookmark

    def _fix(self, bookmark):
        """
        :param str bookmark:
        """
        # connected data
        hyperPositionStored = {}
        hyperPosition = "{0}.hyperPosition".format(bookmark)

        try:
            # get connections with lock state
            if cmds.objExists(hyperPosition):
                connections = cmds.listConnections(hyperPosition) or []
                connections = list(set(connections))
                for connection in connections:
                    state = cmds.lockNode(connection, query=True, lock=True)[0]
                    cmds.lockNode(connection, lock=True)

                    hyperPositionStored[connection] = state

            # delete bookmark
            cmds.delete(bookmark)
        except:
            pass
        finally:
            # reset connections locked state
            for node, state in hyperPositionStored.iteritems():
                cmds.lockNode(node, lock=state)


class EmptyTransform(QualityAssurance):
    """
    All transform will be checked to see if they are empty. When fixing these
    nodes will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Empty Transforms"
        self._message = "{0} transform(s) are empty"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty transforms
        :rtype: generator
        """
        errors = []

        transforms = self.ls(transforms=True, l=True)
        transforms = reference.removeReferenced(transforms)
        transforms = sorted(transforms)
        transforms.reverse()

        for transform in transforms:
            appendToError = False

            # remove existing empty children
            children = cmds.listRelatives(transform, c=True, f=True) or []
            for c in children:
                if c in errors:
                    children.remove(c)

            # continue of transform has children
            if len(children) != 0:
                continue

            # continue if transform is not a transform ( maya bug )
            if cmds.nodeType(transform) != "transform":
                continue

            # append to error list conditions
            connection = cmds.listConnections(transform) or []
            if len(connection) == 0:
                appendToError = True
            elif len(connection) == 1 \
                    and cmds.nodeType(connection[0]) == "displayLayer":
                appendToError = True
            elif len(connection) == 1 \
                    and cmds.nodeType(connection[0]) == "renderLayer":
                appendToError = True

            # append to error list
            if appendToError:
                errors.append(transform)
                yield transform

    def _fix(self, transform):
        """
        :param str transform:
        """
        cmds.delete(transform)


class EmptyDisplayLayer(QualityAssurance):
    """
    All display layers will be checked to see if they are empty. When fixing
    these nodes will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Empty Display Layers"
        self._message = "{0} display layer(s) are empty"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty display layers
        :rtype: generator
        """
        layers = self.ls(type="displayLayer")
        layers = reference.removeReferenced(layers)

        for layer in layers:
            if (
                not cmds.editDisplayLayerMembers(layer, query=True)
                and not layer.endswith("defaultLayer")
            ):
                yield layer

    def _fix(self, layer):
        """
        :param str layer:
        """
        cmds.delete(layer)


class EmptyRenderLayer(QualityAssurance):
    """
    All render layers will be checked to see if they are empty. When fixing
    these nodes will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Empty Render Layers"
        self._message = "{0} render layer(s) are empty"
        self._categories = ["Scene"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty render layers
        :rtype: generator
        """
        layers = self.ls(type="renderLayer")
        layers = reference.removeReferenced(layers)

        for layer in layers:
            if (
                not cmds.editRenderLayerMembers(layer, query=True)
                and not cmds.getAttr("{0}.global".format(layer))
            ):
                yield layer

    def _fix(self, layer):
        """
        :param str layer:
        """
        cmds.delete(layer)


class NonReferencedNamespace(QualityAssurance):
    """
    All nodes will be checked to see if they have a non-referenced namespace.
    When fixing this the namespace will be removed from the node.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Non Referenced Namespaces"
        self._message = "{0} node(s) have a non-referenced namespace"
        self._categories = ["Scene"]
        self._selectable = False

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Nodes that contain a non-referenced namespace
        :rtype: generator
        """
        nodes = self.ls(l=True)
        nodes = reference.removeReferenced(nodes)

        for node in nodes:
            root = path.rootName(node)
            if root.find(":") != -1:
                yield node

    def _fix(self, node):
        """
        :param str node:
        """
        # get namespace
        namespace = path.namespace(node)

        # get node
        cmds.rename(node, path.baseName(node))

        # remove namespace
        if not cmds.namespaceInfo(namespace, listOnlyDependencyNodes=True):
            cmds.namespace(set=":")
            cmds.namespace(removeNamespace=namespace)


class EmptyNamespaces(QualityAssurance):
    """
    All namespaces will be checked to see if they are empty. When fixing
    these namespaces will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Empty Namespaces"
        self._message = "{0} namespace(s) are empty"
        self._categories = ["Scene"]
        self._selectable = False

        self._ignoreNamespaces = ["shared", "UI"]

    # ------------------------------------------------------------------------

    @property
    def ignoreNamespaces(self):
        """
        :return: Namespaces to ignore
        :rtype: list
        """
        return self._ignoreNamespaces

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Empty namespaces
        :rtype: generator
        """
        # set namespace to root
        cmds.namespace(set=":")

        # get all namespaces
        namespaces = cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True)
        namespaces.reverse()

        # loop namespaces
        for ns in namespaces:
            if ns in self.ignoreNamespaces:
                continue

            # yield empty namespaces
            if not cmds.namespaceInfo(ns, listOnlyDependencyNodes=True):
                yield ns

    def _fix(self, namespace):
        """
        :param str namespace:
        """
        cmds.namespace(set=":")
        cmds.namespace(removeNamespace=namespace)
