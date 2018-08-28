from maya import cmds
from ..utils import QualityAssurance, animation, reference


class NotConnectedAnimation(QualityAssurance):
    """
    Animation curves will be checked to see if the output value is connected.
    When fixing this error the non-connected animation curves will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Unused Animation"
        self._message = "{0} animation curve(s) are unused"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves without output connection
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)

        for animCurve in animCurves:
            # check if the output plug is connected
            if cmds.listConnections("{0}.output".format(animCurve)):
                continue

            # yield error
            yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        cmds.delete(animCurve)


class ComponentAnimation(QualityAssurance):
    """
    Meshes will be checked if they have animation curves connected to them.
    When fixing this error the animation curves will be deleted.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Component Animation"
        self._message = "{0} animation curve(s) are connected to a shape"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves connected to meshes
        :rtype: generator
        """
        meshes = self.ls(type="mesh")
        for mesh in meshes:
            # get connected animation curves
            animCurves = cmds.listConnections(
                "{0}.pnts".format(mesh),
                type="animCurve"
            ) or []

            # filter referenced animation curves
            animCurves = reference.removeReferenced(animCurves)

            # yield error
            for animCurve in animCurves:
                yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        cmds.delete(animCurve)


class SubFrameAnimation(QualityAssurance):
    """
    Animation curves will be checked if they have keys set to sub-frames.
    When fixing this error those keys will be rounded to the closest round
    value.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Sub-Frame Animation"
        self._urgency = 1
        self._message = "{0} animation curve(s) have keys in sub-frames"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves with sub-frame keys
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)
        animCurves = animation.removeDrivenAnimCurves(animCurves)

        for animCurve in animCurves:
            frames = cmds.keyframe(
                animCurve,
                query=True,
                timeChange=True
            ) or []

            for f in frames:
                if round(f, 0) != f:
                    yield animCurve
                    break

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        num = cmds.keyframe(animCurve, query=True, keyframeCount=True)
        frames = cmds.keyframe(animCurve, index=(0, num), query=True, tc=True)

        # loop each key
        for i, f in enumerate(frames):
            if round(f, 0) != f:
                cmds.keyframe(animCurve, index=(i,), tc=round(f, 0))


class TemplateAnimation(QualityAssurance):
    """
    Animation curves that are set to template. When fixing this error the
    animation curves will be untemplated.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Template Animation"
        self._message = "{0} animation curve(s) are set to template"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves that have templated keys
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)
        animCurves = animation.removeDrivenAnimCurves(animCurves)

        for animCurve in animCurves:
            size = cmds.getAttr("{0}.ktv".format(animCurve), size=True)

            for i in range(size):
                if cmds.getAttr("{0}.ktv[{1}]".format(animCurve, i), lock=True):
                    yield animCurve
                    break

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        # get number of keys
        size = cmds.getAttr("{0}.ktv".format(animCurve), size=True)

        # unlock each key
        for i in range(size):
            cmds.setAttr("{0}.ktv[{1}]".format(animCurve, i), lock=0)

        # unlock entire channel
        cmds.setAttr("{0}.ktv".format(animCurve), lock=0)


class CleanAnimation(QualityAssurance):
    """
    Animation curves that have unnessecary keys. When fixing this error
    either the unnessecary keys will be removed, or the entire animation
    curve will be deleted if it is a static channel.
    """
    def __init__(self):
        QualityAssurance.__init__(self)

        self._name = "Clean Animation"
        self._message = "{0} animation curve(s) have unnecessary key(s)"
        self._categories = ["Animation"]
        self._selectable = True

    # ------------------------------------------------------------------------

    def evaluateAnimCurve(self, animCurve, angle=0.001, size=0.001):
        """
        Process an animation curve and see if it contains any unnessecary keys
        or if the animation curve can be deleted as a whole. The return value
        is a tuple with the action, either "delete" or "indices", this
        variable can be used to determine which action to take next. And the
        list of indices that can be removed.

        :param str animCurve:
        :param float angle:
        :param float size:
        :return: Action and indices
        :rtype: tuple
        """
        # get in angles
        inAngles = [
            abs(a)
            for a in cmds.keyTangent(
                animCurve, query=True, inAngle=True
            ) or []
        ]

        # get out angles
        outAngles = [
            abs(a)
            for a in cmds.keyTangent(
                animCurve, query=True, outAngle=True
            ) or []
        ]

        # get out tangent types
        outTangentTypes = cmds.keyTangent(
            animCurve, query=True, outTangentType=True
        ) or []

        # get frames and values
        frames = cmds.keyframe(animCurve, query=True, timeChange=True) or []
        values = cmds.keyframe(animCurve, query=True, valueChange=True) or []

        # proces curve data
        indices = []
        for i in range(1, len(frames)-1):

            # is stepped
            stepped = outTangentTypes[i-1] == "step" \
                      and outTangentTypes[i] == "step" \
                      and outTangentTypes[i+1] == "step"

            if stepped \
                or (
                        outAngles[i-1] < angle
                        and inAngles[i] < angle
                        and outAngles[i] < angle
                        and inAngles[i+1] < angle
                    ):

                # get differences between keys
                previousDif = abs(values[i-1] - values[i])
                nextDif = abs(values[i+1] - values[i])

                if (stepped and previousDif < size) \
                    or (
                        not stepped
                        and previousDif < size
                        and nextDif < size
                    ):

                    # append index
                    indices.append(i)

        # remove curves with only 1 key
        if len(frames) <= 1:
            return "delete", None

        # remove curves with keys that are the same
        elif (len(frames) - len(indices)) == 2 \
                and (abs(values[0] - values[-1]) < size) \
                and outAngles[0] < angle \
                and inAngles[-1] < angle:

            return "delete", None

        # remove just specific indices
        elif indices:
            return "indices", indices

        # ignore
        return "pass", []

    # ------------------------------------------------------------------------

    def _find(self):
        """
        :return: Animation curves with unnessecary keys
        :rtype: generator
        """
        animCurves = self.ls(type="animCurve")
        animCurves = reference.removeReferenced(animCurves)
        animCurves = animation.removeDrivenAnimCurves(animCurves)

        for animCurve in animCurves:
            action, _ = self.evaluateAnimCurve(animCurve)
            if action in ["delete", "indices"]:
                yield animCurve

    def _fix(self, animCurve):
        """
        :param str animCurve:
        """
        action, indices = self.evaluateAnimCurve(animCurve)

        if action == "delete":
            # get plugs
            plugs = cmds.listConnections(
                "{0}.output".format(animCurve), p=True
            ) or []

            # get attributes
            attributes = [
                cmds.getAttr(p)
                for p in plugs
            ]

            # delete anim curve
            cmds.delete(animCurve)

            # reset attributes
            for p, a in zip(plugs, attributes):
                if cmds.getAttr(p, lock=True):
                    continue

                cmds.setAttr(p, a)

        elif action == "indices":
            # remove key indices
            for i in indices[::-1]:
                cmds.cutKey(animCurve, clear=True, index=(i, i))
