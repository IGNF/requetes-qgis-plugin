import os

from PyQt5.QtWidgets import QListWidgetItem
from qgis.PyQt.uic import loadUi
from qgis.core import QgsProject

from .mapping_version import *


operateurs = {
    "est egal à": "=",
    "est diffèrent de": "!=",
    "est supérieur à": ">",
    "est supérieur ou égal à": ">=",
    "est inférieur à": "<",
    "est inférieur ou égal à": "<="
}


class RechercheDialog:
    def __init__(self, iface):
        self.champs = None
        self.dlg_recherche = None
        self.dlg_champs_attr = None
        self.iface = iface
        self.layer_sel = None
        self.dico_all_conditions = {}

    # UI===============================================
    def Affiche_dial(self):
        self.dlg_recherche = QDialog(self.iface.mainWindow())
        loadUi(os.path.dirname(__file__) + "/recherche.ui", self.dlg_recherche)
        self.dlg_recherche.setWindowTitle("Recherche")
        # self.dlg_recherche.pushButton_rech.clicked.connect(self.on_recherche)

        # événement changement layer dans mMapLayerComboBox
        # self.dlg_recherche.pushButton_add_layer.clicked.connect(self.on_add_layer)
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
        # slot lors d'un changement de champ sélectionné
        self.dlg_champs_attr.mFieldComboBox.fieldChanged.connect(self.on_champ_changed)
        self.dlg_champs_attr.pushButton_add.clicked.connect(self.on_ajout_condition)
        self.dlg_champs_attr.comboBox_operateur.addItems(operateurs) # les clés du dico

        self.dico_all_conditions.clear()
        self.dlg_champs_attr.exec()
    # UI===============================================

    def onLayerChanged(self,layer):
        self.layer_sel = layer
        self.dico_all_conditions[self.layer_sel.name()] = {"champ":"",
                                                           "operateur":"",
                                                           "valeur":""}
        self.on_add_layer()

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

    # ajout de la condition dans le tableau
    def on_ajout_condition(self):
        # self.dico_all_conditions[self.layer_sel.name()] = "test"
        print("layer = ",self.dico_all_conditions.keys())
        print("champs = ",self.dico_all_conditions[self.layer_sel.name()]["champ"])
        self.dlg_champs_attr.listWidget_affiche_condition.addItem(operateurs.get("est diffèrent de"))

    def on_valide_condition(self):
        print("on valide condition")

    def get_layer_from_layername(self,layer_name):
        layers = QgsProject.instance().mapLayersByName(layer_name)
        return layers[0]

    def get_valeur_from_champ(self,champ):
        # recuperation des valeurs du formulaire de la couche sélectionnée
        layer_field = self.layer_sel.fields().field(champ)
        # Vérifier le type d’éditeur
        editor_setup = layer_field.editorWidgetSetup()
        valeurs_possibles = []

        # CAS TEXTEDIT
        if editor_setup.type() == "TextEdit":
            return None

        # CAS NORMAL (ValueMap etc.)
        for v in editor_setup.config().values():
            if isinstance(v, dict):
                valeurs_possibles.extend(v.values())
            elif isinstance(v, list):
                for elem in v:
                    if isinstance(elem, dict):
                        valeurs_possibles.extend(elem.values())
                    else:
                        valeurs_possibles.append(elem)
            elif isinstance(v, (str, int, float)):
                valeurs_possibles.append(v)
        return valeurs_possibles

    # condition de recherche :
    def on_champ_changed(self):
        champ = self.dlg_champs_attr.mFieldComboBox.currentField()
        self.dico_all_conditions[self.layer_sel.name()] = {"champ":champ}
        # print(f"champ sélectionné = {champ.name()}")
        valeur = self.get_valeur_from_champ(champ)
        print(f"valeurs uniques = {valeur}")
        self.dlg_champs_attr.listWidget_valeur.clear()
        # liste de valeurs
        if valeur is not None:
            self.dlg_champs_attr.listWidget_valeur.addItems([str(v) for v in valeur])
        else:
            # les valeurs sont libres, on met un item editable (texte).
            item = QListWidgetItem("...")
            item.setFlags(item.flags() | ItemIsEditable)
            self.dlg_champs_attr.listWidget_valeur.addItem(item)

