from maya import cmds


def removeDrivenAnimCurves(animCurves):
    """
    Remove set driven animation curves from the list.

    :param list animCurves: List of strings
    :return: Filtered list without set driven anim curves
    :rtype: generator
    """
    for animCurve in animCurves:
        if cmds.listConnections("{0}.input".format(animCurve)):
            continue

        yield animCurve
