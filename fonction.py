import os

from qgis.core import QgsProject


def get_dossier_listes() -> str:
    """
        Retourne le chemin du dossier des listes.
        :return: str
        """
    project = QgsProject.instance()
    chemin_projet = project.fileName()
    dossier_projet = os.path.dirname(chemin_projet)
    dossier_listes = os.path.join(dossier_projet, "LISTES")
    return dossier_listes

# retourne un dictionnaire (cle = layer.name() , valeur = id des selections
def get_dico_selection(layer):
    selection_dict = {}
    # Parcours tous les layers
    for layer in QgsProject.instance().mapLayers().values():
        if layer.type() == layer.VectorLayer:  # seulement les couches vecteurs
            selected_ids = layer.selectedFeatureIds()
            if selected_ids:
                # recuperation des cleabs dorénavant
                # selection_dict[layer.name()] = get_cleabs_from_ids(layer,selected_ids)
                selection_dict[layer.name()] = selected_ids
    return selection_dict