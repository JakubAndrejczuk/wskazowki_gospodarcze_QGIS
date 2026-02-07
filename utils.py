# -*- coding: utf-8 -*-
from qgis.core import QgsProject

def load_opis_text(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return 'Brak opisu (plik "Opis.txt" w folderze wtyczki).'

def set_only_layers_visible_by_ids(visible_ids):
    """
    Ustaw widoczność tylko dla warstw o podanych ID.
    Pozostałe warstwy w projekcie będą ukryte.
    """
    root = QgsProject.instance().layerTreeRoot()
    for node in root.findLayers():
        node.setItemVisibilityChecked(node.layerId() in visible_ids)
