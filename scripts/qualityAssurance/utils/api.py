from maya import cmds, OpenMaya


def toMObject(node):
    """
    Convert a node into a OpenMaya.MObject.

    :param str node:
    :return: MObject of parsed node
    :rtype: OpenMaya.MObject
    """
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(node)
    obj = OpenMaya.MObject()
    selectionList.getDependNode(0, obj)
    
    return obj


def toMDagPath(node):
    """
    Convert a node into a OpenMaya.MDagPath.

    :param str node:
    :return: MDagPath of parsed node
    :rtype: OpenMaya.MDagPath
    """
    obj = toMObject(node)
    if obj.hasFn(OpenMaya.MFn.kDagNode):
        dag = OpenMaya.MDagPath.getAPathTo(obj)
        return dag
