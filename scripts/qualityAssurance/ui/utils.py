import os
from maya import OpenMaya, OpenMayaUI, cmds


# ----------------------------------------------------------------------------


# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4") or type(qtVersion) not in [str, unicode]:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken


# ----------------------------------------------------------------------------


FONT = QFont()
FONT.setFamily("Consolas")

BOLT_FONT = QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)


# ----------------------------------------------------------------------------


ALIGN_LEFT_STYLESHEET = "QPushButton{text-align: left}"
URGENCY_STYLESHEET = {
    0: "QPushButton{ background-color: green;}",
    1: "QPushButton{ background-color: orange;}",
    2: "QPushButton{ background-color: red;}",
}

CHECK_ICON = ":/checkboxOff.png"
SELECT_ICON = ":/redSelect.png"
FIX_ICON = ":/interactivePlayback.png"

COLLAPSE_ICONS = {
    True: ":/arrowDown.png",
    False: ":/arrowRight.png"
}


# ----------------------------------------------------------------------------


def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)
    
    return window  


# ----------------------------------------------------------------------------


def getIconPath(name):
    """
    Get an icon path based on file name. All paths in the XBMLANGPATH variable
    processed to see if the provided icon can be found.

    :param str name:
    :return: Icon path
    :rtype: str/None
    """
    for path in os.environ.get("XBMLANGPATH").split(os.pathsep):
        iconPath = os.path.join(path, name)
        if os.path.exists(iconPath):
            return iconPath.replace("\\", "/")
