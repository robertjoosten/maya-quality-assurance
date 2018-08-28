import sys
import traceback
from maya import cmds, OpenMaya
from . import decorators, undo, path


class QualityAssurance(object):
    """
    This is the base class that can be used to generate your own quality
    assurance checks. Key variables can be overwritten and a _find and _fix
    function should be implemented to complete the check, otherwise the class
    will not register as findable or checkable.
    """
    def __init__(self):
        # variables
        self._name = ""
        self._urgency = 2
        self._categories = []

        self._message = ""
        self._information = self.__doc__

        self._selectable = False
        self._onSelected = False

        self._errors = []

    # ------------------------------------------------------------------------

    @property
    def name(self):
        """
        :return: Quality assurance name
        :rtype: str
        """
        return self._name

    @property
    @decorators.ifNoErrorsReturn(0)
    def state(self):
        """
        If no errors can be found the state of the check is neutral which is
        set to a value of 0. Different levels of urgency can be implemented
        with increasing values.

        :return: Current state of quality assurance
        :rtype: int
        """
        return self._urgency

    @property
    def categories(self):
        """
        :return: Categories error check should belong too
        :rtype: list
        """
        return self._categories

    # ------------------------------------------------------------------------

    @property
    @decorators.ifNoErrorsReturn("")
    def message(self):
        """
        Message informing the user about the state of the check and the number
        of errors. If not errors are found and empty string is returned.

        :return: Quality assurance message
        :rtype: str
        """
        return self._message.format(len(self.errors))

    @property
    def information(self):
        """
        :return: Quality assurance information
        :rtype: list
        """
        return self._information

    # ------------------------------------------------------------------------

    @property
    def errors(self):
        """
        :return: Quality assurance error list
        :rtype: list
        """
        return self._errors

    # ------------------------------------------------------------------------

    def isFindable(self):
        """
        A quality assurance check becomes findable if a _find method is
        implemented,

        :return: Findable state of quality assurance check
        :rtype: bool
        """
        return True if "_find" in dir(self) else False

    def find(self):
        """
        Runs the _find method and appends all of the errors found to the
        error list.
        """
        # check if is fixable
        if not self.isFindable():
            raise RuntimeError(
                "{0} doesn't allow for error finding!".format(self.name)
            )

        # reset errors list
        self._errors = []

        # find errors
        for error in self._find():
            if error in self.errors:
                continue

            self.errors.append(error)

    # ------------------------------------------------------------------------

    def isFixable(self):
        """
        A quality assurance check becomes fixable if a _fix method is
        implemented,

        :return: Fixable state of quality assurance check
        :rtype: bool
        """
        return True if "_fix" in dir(self) else False

    def fix(self):
        """
        Loops over each of the errors found and runs the _fix method on each
        error. The entire function is wrapped in an undo block for easy
        undoing. Each fix is also wrapped in a try function, meaning that if
        an error cannot be fixed, it will remain in the error list but it
        error the application. The _fix method should only take in 1 argument.
        """
        # check if is fixable
        if not self.isFixable():
            raise RuntimeError(
                "{0} doesn't allow for error fixing!".format(self.name)
            )

        # remove errors
        with undo.UndoContext():
            for error in self.errors[:]:
                # remove objects that might have been deleted in other
                # quality assurance checks.

                if self.isSelectable() and (
                        type(error) in [str, unicode]
                        and not cmds.objExists(error)
                ):
                    self._errors.remove(error)
                    continue

                try:
                    self._fix(error)
                    self._errors.remove(error)
                except:
                    traceback.print_exc()

    # ------------------------------------------------------------------------

    @property
    def onSelected(self):
        """
        :return: Only run quality assurance check in selection
        :rtype: bool
        """
        return self._onSelected

    @onSelected.setter
    def onSelected(self, value):
        """
        :param bool value: Only run on selection state
        """
        self._onSelected = value

    # ------------------------------------------------------------------------

    def isSelectable(self):
        """
        :return: If the error list is selectable
        :rtype: bool
        """
        return self._selectable

    def select(self):
        """
        Select all current entries of the error list.
        """
        if self.isSelectable() and self.errors:
            cmds.select(path.asFlatList(self.errors))

    # ------------------------------------------------------------------------

    def ls(self, **kwargs):
        """
        Subclass of Maya's ls command. This command should be used to get the
        nodes in a quality assurance check. This will automatically take into
        account of the check should only run on selected objects or not.

        :return: Object list
        :rtype: list
        """
        return cmds.ls(sl=self.onSelected, **kwargs) or []

    def lsApi(self, nodeType=OpenMaya.MFn.kTransform):
        """
        Get a OpenMaya.MItSelectionList object. This command should be used to
        get the nodes in a quality assurance check. This will automatically
        take into account of the check should only run on selected objects or
        not.

        :return: Object list
        :rtype: OpenMaya.MItSelectionList
        """
        selectionList = OpenMaya.MSelectionList()

        if self.onSelected:
            # populate selection list with active selection
            OpenMaya.MGlobal.getActiveSelectionList(selectionList)
        else:
            # populate selection list with all object of nodetype
            iterator = OpenMaya.MItDependencyNodes(nodeType)
            while not iterator.isDone():
                obj = iterator.thisNode()
                selectionList.add(obj)
                iterator.next()

        return OpenMaya.MItSelectionList(selectionList, nodeType)
