import os

from qgis.gui import QgisInterface
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QEvent, QObject, Qt

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "simple_ban_dialog_base.ui")
)


class StayOnTopEventFilter(QObject):
    def __init__(self, dialog, qgis_main_window):
        super(StayOnTopEventFilter, self).__init__()
        self.dialog = dialog
        self.qgis_main_window = qgis_main_window

    def eventFilter(self, watched, event):
        if (
            watched == self.qgis_main_window
            and event.type() == QEvent.Type.WindowActivate
        ):
            if self.dialog.isVisible() and not self.dialog.isActiveWindow():
                self.dialog.raise_()
        return super(StayOnTopEventFilter, self).eventFilter(watched, event)


class SimbleBanDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface: QgisInterface, parent=None):
        super(SimbleBanDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.event_filter = StayOnTopEventFilter(self, iface.mainWindow())
        self.iface.mainWindow().installEventFilter(self.event_filter)
