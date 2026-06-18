import os

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUi


class RechercheDialog:
    def __init__(self, iface):
        self.dlg_recherche = None
        self.iface = iface

    def Affiche_dial(self):
        self.dlg_recherche = QDialog(self.iface.mainWindow())
        loadUi(os.path.dirname(__file__) + "/recherche.ui", self.dlg_recherche)
        self.dlg_recherche.setWindowTitle("Recherche")
        # self.dlg_recherche.pushButton_rech.clicked.connect(self.on_recherche)
        # self.dlg_recherche.pushButton_req_unique.clicked.connect(self.on_req_unique)
        # self.dlg_recherche.pushButton_reg_enchaine.clicked.connect(self.on_req_enchaine)
        self.dlg_recherche.show()