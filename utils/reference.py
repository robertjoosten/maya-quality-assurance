from maya import cmds


def removeReferenced(nodes):
    """
    Remove all referenced nodes from list.

    :param list nodes: List of strings
    :return: Filtered list without referenced nodes
    :rtype: generator
    """
    for node in nodes:
        if cmds.referenceQuery(node, inr=True):
            continue

        yield node
