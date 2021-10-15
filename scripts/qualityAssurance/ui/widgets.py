from . import utils
from .. import checks, collections


class CollectionsWidget(utils.QWidget):
    currentIndexChanged = utils.Signal(unicode)

    def __init__(self, parent, collection):
        utils.QWidget.__init__(self, parent)

        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create combobox
        overview = collections.getCollectionsCategories()

        self.collection = utils.QComboBox(self)
        self.collection.addItems(overview)
        self.collection.setCurrentIndex(
            overview.index(collection)
            if collection in overview
            else 0
        )
        self.collection.currentIndexChanged.connect(self.trigger)
        self.collection.setFont(utils.FONT)
        layout.addWidget(self.collection)

    # ------------------------------------------------------------------------

    def trigger(self):
        """
        Trigger currentIndexChanged signal.
        """
        self.currentIndexChanged.emit(self.collection.currentText())


class DropDownWidget(utils.QWidget):
    switchVisiblity = utils.Signal()

    def __init__(self, parent, category):
        utils.QWidget.__init__(self, parent)

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create icon
        self.icon = utils.QPushButton(self)
        self.icon.setFixedSize(utils.QSize(24, 24))
        self.icon.setFlat(True)
        self.icon.released.connect(self.switchVisiblity.emit)
        layout.addWidget(self.icon)

        # set icon
        self.setIcon(True)

        # create category
        cat = utils.QLabel(self)
        cat.setFont(utils.BOLT_FONT)
        cat.setText(category)
        layout.addWidget(cat)

    # ------------------------------------------------------------------------

    def setIcon(self, state):
        """
        Set icon based on the state. The icon variables are stored in the
        COLLAPSE_ICONS variable.

        :param bool state:
        """
        self.icon.setIcon(
            utils.QIcon(
                utils.COLLAPSE_ICONS.get(state)
            )
        )


class CategoryWidget(utils.QWidget):
    def __init__(self, parent, category):
        utils.QWidget.__init__(self, parent)

        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create collapse bar
        self.collapse = DropDownWidget(self, category)
        self.collapse.switchVisiblity.connect(self.switchVisibility)
        layout.addWidget(self.collapse)

        # create widget and layout
        self.widget = utils.QWidget(self)
        layout.addWidget(self.widget)

        self.layout = utils.QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.setSpacing(3)

    # ------------------------------------------------------------------------

    def addWidget(self, widget):
        """
        :param widget:
        """
        self.layout.addWidget(widget)

    # ------------------------------------------------------------------------

    def switchVisibility(self):
        """
        Toggle the visibilty of the widget and changing the icon of the of the
        collapse widget.
        """
        state = not self.widget.isVisible()

        self.collapse.setIcon(state)
        self.widget.setVisible(state)


class CheckWidget(utils.QWidget):
    def __init__(self, parent, check, number):
        utils.QWidget.__init__(self, parent)

        # variables
        self.check = check
        self.toolTipText = "<b>{0}</b>:<br>{1}".format(
            self.check.name,
            self.check.information
        )

        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # create number
        num = utils.QLabel(self)
        num.setFont(utils.FONT)
        num.setText("{:03d}".format(number))
        num.setFixedSize(utils.QSize(25, 16))
        layout.addWidget(num)

        # create button
        self.urgency = utils.QPushButton(self)
        self.urgency.setMinimumSize(16, 16)
        self.urgency.setMaximumSize(16, 16)
        self.urgency.setFlat(True)
        self.urgency.setIcon(utils.QIcon(utils.CHECK_ICON))
        self.urgency.setToolTip(self.toolTipText)
        self.urgency.released.connect(self.doFind)
        layout.addWidget(self.urgency)

        if not self.check.isFindable():
            self.urgency.setEnabled(False)

        # create status
        self.status = utils.QLabel(self)
        self.status.setFont(utils.FONT)
        self.status.setText(self.check.name)
        self.status.setToolTip(self.toolTipText)
        layout.addWidget(self.status)

        # create selection only
        self.selectionOnly = utils.QCheckBox(self)
        self.selectionOnly.setMinimumSize(16, 16)
        self.selectionOnly.setMaximumSize(16, 16)
        self.selectionOnly.setToolTip("Perform Check on Selection Only")
        layout.addWidget(self.selectionOnly)

        if not self.check.isSelectable():
            self.selectionOnly.setEnabled(False)

        # create select
        self.select = utils.QPushButton(self)
        self.select.setMinimumSize(16, 16)
        self.select.setMaximumSize(16, 16)
        self.select.setFlat(True)
        self.select.setIcon(utils.QIcon(utils.SELECT_ICON))
        self.select.setEnabled(False)
        self.select.released.connect(self.check.select)
        layout.addWidget(self.select)

        # create fix
        self.fix = utils.QPushButton(self)
        self.fix.setMinimumSize(16, 16)
        self.fix.setMaximumSize(16, 16)
        self.fix.setFlat(True)
        self.fix.setIcon(utils.QIcon(utils.getIconPath("QA_fix.png")))
        self.fix.released.connect(self.doFix)
        self.fix.setEnabled(False)
        layout.addWidget(self.fix)

    # ------------------------------------------------------------------------

    def doFind(self):
        """
        Run the find. The selection state is taken into account at this state.
        Once the find is ran, the refresh function will be called to update
        the ui.
        """
        self.check.onSelected = self.selectionOnly.isChecked()
        self.check.find()
        self.refresh()

    def doFix(self):
        """
        Run the fix. Once the fix is ran, the refresh function will be called
        to update the ui.
        """
        self.check.fix()
        self.refresh()

    # ------------------------------------------------------------------------

    def refresh(self):
        """
        Refresh the widget based on the current status of the check. Urgency
        indicators will be set, status text changed, selectable and fix button
        enabled or disabled.
        """
        # update urgency
        self.urgency.setIcon(utils.QIcon())
        self.urgency.setFlat(False)
        self.urgency.setStyleSheet(
            utils.URGENCY_STYLESHEET.get(self.check.state)
        )

        # update status
        self.status.setText(
            self.check.message if self.check.message else self.check.name
        )

        # update selectable
        self.select.setEnabled(False)
        if self.check.errors and self.check.isSelectable():
            self.select.setEnabled(True)

        # update fixable
        self.fix.setEnabled(False)
        if self.check.errors and self.check.isFixable():
            self.fix.setEnabled(True)


class QualityAssuranceWidget(utils.QWidget):
    def __init__(self, parent, collection="Default"):
        utils.QWidget.__init__(self, parent)

        # variable
        self.widgets = []

        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # create scroll
        scrollArea = utils.QScrollArea(self)
        scrollArea.setWidgetResizable(True)

        self.widget = utils.QWidget(self)
        self.layout = utils.QVBoxLayout(self.widget)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(3)

        scrollArea.setWidget(self.widget)
        layout.addWidget(scrollArea)

        # create spacer
        spacer = utils.QSpacerItem(
            1,
            1,
            utils.QSizePolicy.Minimum,
            utils.QSizePolicy.Expanding
        )

        self.layout.addItem(spacer)

        # loop widget
        loop = utils.QWidget(self)
        layout.addWidget(loop)

        loopLayout = utils.QHBoxLayout(loop)
        loopLayout.setContentsMargins(0, 0, 0, 0)
        loopLayout.setSpacing(5)

        # create check all
        findAll = utils.QPushButton(loop)
        findAll.setFont(utils.FONT)
        findAll.setText("Find All")
        findAll.released.connect(self.doFindAll)
        loopLayout.addWidget(findAll)

        # create fix all
        fixAll = utils.QPushButton(loop)
        fixAll.setFont(utils.FONT)
        fixAll.setText("Fix All")
        fixAll.released.connect(self.doFixAll)
        loopLayout.addWidget(fixAll)

        # add checks
        self.refresh(collection)

    # ------------------------------------------------------------------------

    def doFindAll(self):
        """
        Loop over all widgets and see if the check button is enabled. If this
        is the case the check function can be ran.
        """
        for widget in self.widgets:
            if not widget.urgency.isEnabled():
                continue

            widget.doFind()
            self.repaint()
            utils.QCoreApplication.processEvents()

    def doFixAll(self):
        """
        Loop over all widgets and see if the fix button is enabled. If this
        is the case the fix function can be ran.
        """
        for widget in self.widgets:
            if not widget.fix.isEnabled():
                continue

            widget.doFix()
            self.repaint()
            QtCore.QCoreApplication.processEvents()

    # ------------------------------------------------------------------------

    def clear(self):
        """
        Remove all of the widgets from the layout apart from the last item
        which is a spacer item.
        """
        for i in reversed(range(self.layout.count() - 1)):
            item = self.layout.itemAt(i)
            item.widget().deleteLater()

    # ------------------------------------------------------------------------

    def refresh(self, collection):
        """
        Clear the entire UI and populate it with the checks that are part of
        the collection parsed in as an argument.

        :param str collection:
        """
        # clear ui
        self.clear()
        self.widgets = []

        # get checks
        data = checks.getChecksFromCollection(collection)
        number = 1
        for categoryName, checkList in data.iteritems():
            # create category
            category = CategoryWidget(self, categoryName)
            self.layout.insertWidget(self.layout.count()-1, category)

            # create checks
            for check in checkList:
                widget = CheckWidget(self, check, number)
                self.widgets.append(widget)

                # add check to category
                category.addWidget(widget)
                number += 1
