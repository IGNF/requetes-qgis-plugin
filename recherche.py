import os

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUi
from qgis.core import QgsProject, QgsFeatureFilterModel

OPERTATEUR = ["est egal à","est diffèrent de","est inférieur à","est inférieur ou égal à",
              "est supérieur à","est supérieur ou égal  à"]


class RechercheDialog:
    def __init__(self, iface):
        self.champs = None
        self.dlg_recherche = None
        self.dlg_champs_attr = None
        self.iface = iface
        self.layer_sel = None

    # UI===============================================
    def Affiche_dial(self):
        self.dlg_recherche = QDialog(self.iface.mainWindow())
        loadUi(os.path.dirname(__file__) + "/recherche.ui", self.dlg_recherche)
        self.dlg_recherche.setWindowTitle("Recherche")
        # self.dlg_recherche.pushButton_rech.clicked.connect(self.on_recherche)

        # événement changement layer dans mMapLayerComboBox
        self.dlg_recherche.pushButton_add_layer.clicked.connect(self.on_add_layer)
        self.dlg_recherche.pushButton_suppr_layer.clicked.connect(self.on_suppr_layer)
        self.dlg_recherche.mMapLayerComboBox.layerChanged.connect(self.onLayerChanged)
        self.dlg_recherche.listWidget_layer.itemDoubleClicked.connect(self.on_doubleclick_layer)

        self.dlg_recherche.show()
        self.layer_sel = self.dlg_recherche.mMapLayerComboBox.currentLayer()

    def Affiche_dial_champs_attr(self):
        self.dlg_champs_attr = QDialog(self.iface.mainWindow())
        loadUi(os.path.dirname(__file__) + "/conditions.ui", self.dlg_champs_attr)
        self.dlg_champs_attr.setWindowTitle("Conditions")
        self.dlg_champs_attr.pushButton_ok.clicked.connect(self.on_valide_condition)

        text = f"Chercher les objets <span style='color:red'>{self.layer_sel.name()}</span> dont :"
        self.dlg_champs_attr.label_layer.setText(text)

        # init combobox
        self.dlg_champs_attr.mFieldComboBox.setLayer(self.layer_sel)
        self.dlg_champs_attr.comboBox_operateur.addItems(OPERTATEUR)

        self.dlg_champs_attr.exec()
    # UI===============================================

    def onLayerChanged(self,layer):
        self.layer_sel = layer

    def on_add_layer(self):
        self.dlg_recherche.listWidget_layer.addItem(self.layer_sel.name())

    def on_suppr_layer(self):
        index = self.dlg_recherche.listWidget_layer.currentRow()
        self.dlg_recherche.listWidget_layer.takeItem(index)

    def on_doubleclick_layer(self,layer):
        print(f"clic layer = {layer.text()}")
        self.layer_sel = self.get_layer_from_layername(layer.text())
        # champs = self.get_champ_from_layer(self.layer_sel)


        self.Affiche_dial_champs_attr()


    def on_valide_condition(self):
        print("on valide condition")

    def get_layer_from_layername(self,layer_name):
        layers = QgsProject.instance().mapLayersByName(layer_name)
        return layers[0]

    def get_champ_from_layer(self,layer):
        self.champs = [field.name() for field in layer.fields()]
        return self.champs


    def get_valeur_from_champ(self,champ):
        # layers = QgsProject.instance().mapLayersByName(self.layer_sel.text())
        # idx = layers[0].fields().indexOf(champ)
        # valeurs_uniques = layers[0].uniqueValues(idx)
        # print(valeurs_uniques)
        # return valeurs_uniques
        pass

