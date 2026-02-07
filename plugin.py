# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QLocale, QObject
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis import processing
from qgis.core import QgsProject
import os

from .algorithm import WskazowkiGospodarczeAlg
from .utils import set_only_layers_visible_by_ids

class WskazowkiGospodarczePlugin(QObject):
    """
    Klik w ikonę:
      1) otwiera natywne okno Processing z prawym panelem opisu (shortHelpString),
      2) po dodaniu wyników automatycznie ustawia widoczność tylko dla 'wydz_wsk' i 'zreb_wsk'.
    """
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.action = None
        self.plugin_dir = os.path.dirname(__file__)
        self._conn = None  # uchwyt do sygnału layersAdded

        # i18n (opcjonalnie)
        locale = QLocale.system().name()
        self.translator = QTranslator()
        qm_path = os.path.join(self.plugin_dir, 'i18n', f'{locale}.qm')
        if os.path.exists(qm_path):
            self.translator.load(qm_path)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon_path), 'Wskazówki gospodarcze', self.iface.mainWindow())
        self.action.setToolTip('Uruchom algorytm w natywnym oknie Processing')
        self.action.triggered.connect(self._open_native_processing)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('Wskazówki gospodarcze', self.action)

    def unload(self):
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu('Wskazówki gospodarcze', self.action)
        self._disconnect_layer_listener()

    # --- natywne okno Processing + automatyczna kontrola widoczności ---
    def _open_native_processing(self):
        try:
            # 1) nasłuch dodawania warstw (zadziała po uruchomieniu algorytmu z okna)
            self._connect_layer_listener()

            # 2) natywne okno Processing – opis jest w shortHelpString() algorytmu
            alg = WskazowkiGospodarczeAlg()
            processing.execAlgorithmDialog(alg)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), 'Błąd', f'Nie można otworzyć okna Processing:\n{e}')

    def _connect_layer_listener(self):
        self._disconnect_layer_listener()
        QgsProject.instance().layersAdded.connect(self._on_layers_added)
        # dodatkowo, gdyby warstwy zostały dodane pojedynczo:
        QgsProject.instance().layerWasAdded.connect(self._on_single_layer_added)

    def _disconnect_layer_listener(self):
        try:
            QgsProject.instance().layersAdded.disconnect(self._on_layers_added)
        except Exception:
            pass
        try:
            QgsProject.instance().layerWasAdded.disconnect(self._on_single_layer_added)
        except Exception:
            pass

    def _on_single_layer_added(self, layer):
        # Przekieruj do wspólnej logiki
        self._apply_visibility_if_ready()

    def _on_layers_added(self, layers):
        # Po każdej paczce dodanych warstw spróbuj zastosować widoczność
        self._apply_visibility_if_ready()

    def _apply_visibility_if_ready(self):
        """
        Szuka w projekcie warstw o nazwach 'wydz_wsk' i 'zreb_wsk'.
        Gdy obie są już wczytane – ustawia widoczność tylko na nich i odłącza nasłuchiwanie.
        """
        project = QgsProject.instance()
        wydz_id = None
        zreb_id = None

        for lyr in project.mapLayers().values():
            nm = (lyr.name() or '').strip().lower()
            if nm == 'wydz_wsk':
                wydz_id = lyr.id()
            elif nm == 'zreb_wsk':
                zreb_id = lyr.id()

        if wydz_id or zreb_id:
            visible_ids = [i for i in (wydz_id, zreb_id) if i]
            set_only_layers_visible_by_ids(visible_ids)

            # Jeśli obie są już obecne – możemy się rozłączyć
            if wydz_id and zreb_id:
                self._disconnect_layer_listener()
