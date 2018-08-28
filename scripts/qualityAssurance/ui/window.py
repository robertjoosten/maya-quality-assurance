from . import utils, widgets


class QualityAssuranceWindow(utils.QWidget):
    def __init__(self, parent, collection):
        utils.QWidget.__init__(self, parent)

        # set ui
        self.setParent(parent)
        self.setWindowFlags(utils.Qt.Window)

        self.setWindowTitle("Quality Assurance")
        self.setWindowIcon(
            utils.QIcon(utils.getIconPath("QA_icon.png"))
        )
        self.resize(500, 500)

        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # add collections
        self.collections = widgets.CollectionsWidget(self, collection)
        layout.addWidget(self.collections)

        # add container
        self.container = widgets.QualityAssuranceWidget(self, collection)
        layout.addWidget(self.container)

        # connections
        self.collections.currentIndexChanged.connect(self.container.refresh)


def show(collection="modelling"):
    qa = QualityAssuranceWindow(utils.mayaWindow(), collection)
    qa.show()
