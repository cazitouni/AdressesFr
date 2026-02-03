import json
import os.path

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject,
)
from qgis.gui import QgsVertexMarker
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTranslator, QUrl
from qgis.PyQt.QtGui import QColor, QIcon, QPixmap
from qgis.PyQt.QtWidgets import QAction, QCompleter, QErrorMessage, QSplashScreen

from .resources import *
from .simple_ban_dialog import SimbleBanDialog


class AdressesFr:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "AdressesFr_{}.qm".format(locale)
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        self.actions = []
        self.menu = self.tr("Recherche d'adresse simple (BAN)")
        self.first_start = None

    def tr(self, message):
        return QCoreApplication.translate("AdressesFr", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ":/plugins/simple_ban/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("Recherche d'adresse"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr("Recherche d'adresse simple (BAN)"), action
            )
            self.iface.removeToolBarIcon(action)

    def closeEvent(self, event):
        self.deleteMarker()

    def run(self):
        self.dlg = SimbleBanDialog(self.iface)
        self.dlg.rejected.connect(self.deleteMarker)
        self.manager = QNetworkAccessManager()
        self.completer = QCompleter(["", "", "", "", ""])
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setMaxVisibleItems(5)
        self.dlg.barre.setCompleter(self.completer)
        self.model = self.completer.model()
        self.dlg.closeEvent = self.closeEvent
        self.error_dialog = QErrorMessage()
        self.typing_timer = QtCore.QTimer()
        self.typing_timer.setSingleShot(True)
        self.dlg.barre.textEdited.connect(self.start_typing_timer)
        self.typing_timer.timeout.connect(self.completion)
        self.markers = []
        self.dlg.recherche.clicked.connect(self.recherche)
        self.dlg.show()

    def onReplyReceived(self):
        listeAddr = []
        try:
            r = self.r.readAll()
            json_object = json.loads(r.data())
            for feature in json_object["features"]:
                listeAddr.append(str(feature["properties"]["label"]))
            if len(listeAddr) >= 1:
                self.model.setStringList(listeAddr)
            self.dlg.recherche.setEnabled(True)
        except Exception:
            self.dlg.recherche.setEnabled(True)
            pass

    def onReplyReceivedSec(self):
        try:
            r = self.r.readAll()
            json_object = json.loads(r.data())
            x = json_object["features"][0]["geometry"]["coordinates"][0]
            y = json_object["features"][0]["geometry"]["coordinates"][1]
            projetCrs = QgsProject.instance().crs()
            ptsCrs = QgsCoordinateReferenceSystem(4326)
            transform = QgsCoordinateTransform(ptsCrs, projetCrs, QgsProject.instance())
            coord = transform.transform(QgsPointXY(x, y))
            self.iface.mapCanvas().setCenter(coord)
            self.iface.mapCanvas().zoomScale(1000)
            self.deleteMarker()
            m1 = QgsVertexMarker(self.iface.mapCanvas())
            m1.setCenter(coord)
            m1.setColor(QColor(255, 0, 0))
            m1.setIconSize(10)
            m1.setIconType(QgsVertexMarker.ICON_X)
            m1.setPenWidth(3)
            self.markers.append(m1)
            self.iface.mapCanvas().refresh()
            self.dlg.recherche.setEnabled(True)
        except Exception:
            self.dlg.recherche.setEnabled(True)
            pass

    def completion(self):
        if self.dlg.barre.text():
            url = QUrl(
                "https://data.geopf.fr/geocodage/search/?q={}&limit=5".format(
                    self.dlg.barre.text()
                )
            )
            try:
                self.r = self.manager.get(QNetworkRequest(url))
                self.r.finished.connect(self.onReplyReceived)
                self.dlg.recherche.setEnabled(False)
            except Exception:
                self.dlg.recherche.setEnabled(True)
                self.iface.messageBar().pushMessage("Echec de la Requête")
                return

    def recherche(self):
        self.deleteMarker()
        url = QUrl(
            "https://data.geopf.fr/geocodage/search/?q={}&limit=1".format(
                self.dlg.barre.text()
            )
        )
        try:
            self.r = self.manager.get(QNetworkRequest(url))
            self.r.finished.connect(self.onReplyReceivedSec)
            self.dlg.recherche.setEnabled(False)
        except Exception:
            self.dlg.recherche.setEnabled(True)
            self.iface.messageBar().pushMessage("Echec de la Requête")
            return

    def deleteMarker(self):
        canvas = self.iface.mapCanvas()
        for mark in self.markers:
            canvas.scene().removeItem(mark)
        canvas.refresh()

    def start_typing_timer(self):
        self.typing_timer.start(300)
