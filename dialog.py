# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QPushButton, QWidget, QTextEdit, QLabel, QCheckBox
)
from qgis.PyQt.QtGui import QPalette, QColor
from qgis.gui import QgsMapLayerComboBox, QgsFileWidget
from qgis.core import QgsMapLayerProxyModel
import os

from .utils import load_opis_text

class WskazowkiGospodarczeDialog(QDialog):
    # Sygnały dla pluginu:
    execNativeProcessingRequested = pyqtSignal()
    runRequested = pyqtSignal(dict)

    def __init__(self, plugin_dir):
        super().__init__()
        self.setWindowTitle('Wskazówki gospodarcze')
        self.resize(900, 520)

        self.plugin_dir = plugin_dir

        main = QHBoxLayout(self)

        # Lewa kolumna – parametry
        left = QWidget(self)
        left_layout = QVBoxLayout(left)
        form = QFormLayout()
        left_layout.addLayout(form)

        # Warstwy wejściowe
        self.in_form = QgsMapLayerComboBox(self)
        self.in_form.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.in_form.setAllowEmptyLayer(False)

        self.in_wydz = QgsMapLayerComboBox(self)
        self.in_wydz.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.in_wydz.setAllowEmptyLayer(False)

        self.in_zreb = QgsMapLayerComboBox(self)
        self.in_zreb.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.in_zreb.setAllowEmptyLayer(False)

        # Pliki stylów (opcjonalne)
        self.qml_wydz = QgsFileWidget(self)
        self.qml_wydz.setFilter('QGIS Layer Style (*.qml);;Wszystkie pliki (*.*)')
        self.qml_zreb = QgsFileWidget(self)
        self.qml_zreb.setFilter('QGIS Layer Style (*.qml);;Wszystkie pliki (*.*)')

        form.addRow('wskazówki gospodarcze (formularz BO):', self.in_form)
        form.addRow('wydz_pol (pochodne):', self.in_wydz)
        form.addRow('zreb_pol (pochodne):', self.in_zreb)
        form.addRow('wydz_wsk.qml:', self.qml_wydz)
        form.addRow('zreb_wsk.qml:', self.qml_zreb)

        # Checkbox na dole
        self.cb_visual = QCheckBox('Wizualizacja wykonania wskazówek', self)
        self.cb_visual.setChecked(False)
        left_layout.addWidget(self.cb_visual)

        # Przyciski akcji
        btns = QDialogButtonBox(self)
        btns.setStandardButtons(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)

        self.btn_native = QPushButton('Użyj natywnego okna Processing')
        self.btn_run = QPushButton('Uruchom')
        self.btn_native.clicked.connect(self.execNativeProcessingRequested.emit)
        self.btn_run.clicked.connect(self._emit_run)

        left_layout.addWidget(self.btn_native)
        left_layout.addWidget(self.btn_run)
        left_layout.addWidget(btns)

        # Prawa kolumna – opis
        right = QWidget(self)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.lbl_opis = QLabel('Opis', self)
        # (opcjonalnie) wymuś czarną czcionkę także na etykiecie:
        self.lbl_opis.setStyleSheet("QLabel { color: #000000; }")
        right_layout.addWidget(self.lbl_opis)

        self.text = QTextEdit(self)
        self.text.setObjectName("opisText")
        self.text.setReadOnly(True)

        # --- Wymuszenie białego tła i czarnej czcionki (maksymalna odporność na motywy) ---
        # 1) StyleSheet o wysokiej specyficzności (po ID):
        self.text.setStyleSheet(
            "#opisText { background: #ffffff; color: #000000; }"
        )
        # 2) Paleta dla wszystkich stanów + wypełnianie tła
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            pal = self.text.palette()
            pal.setColor(group, QPalette.Base, QColor(255, 255, 255))  # tło edytora
            pal.setColor(group, QPalette.Text, QColor(0, 0, 0))        # kolor tekstu
            self.text.setPalette(pal)

        self.text.setAutoFillBackground(True)
        # 3) To samo na viewport(), z którego rysuje QTextEdit:
        vp = self.text.viewport()
        vp.setAutoFillBackground(True)
        vp_pal = vp.palette()
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            vp_pal.setColor(group, QPalette.Base, QColor(255, 255, 255))
            vp_pal.setColor(group, QPalette.Text, QColor(0, 0, 0))
        vp.setPalette(vp_pal)
        # 4) (opcjonalnie) „odcięcie” dziedziczenia tła ze stylu aplikacji:
        self.text.setAttribute(Qt.WA_StyledBackground, True)
        # -------------------------------------------------------------------------------

        right_layout.addWidget(self.text, 1)

        opis_path = os.path.join(self.plugin_dir, 'Opis.txt')
        self.text.setPlainText(load_opis_text(opis_path))

        # Złożenie
        main.addWidget(left, 1)
        main.addWidget(right, 1)

    def _emit_run(self):
        # Zbierz parametry algorytmu (klucze zgodne z definicją w algorithm.py)
        params = {
            'wskazwki_gospodarcze_formularz_bo': self.in_form.currentLayer(),
            'wydz_pol_pochodne': self.in_wydz.currentLayer(),
            'zreb_pol_pochodne': self.in_zreb.currentLayer(),
            # Flaga wizualizacji wykonania wskazówek
            'wizualizacja_wykonania_wskazowek': self.cb_visual.isChecked(),
            # Sinki: QGIS może utworzyć wyniki tymczasowe
            'Wydz_wsk': 'TEMPORARY_OUTPUT',
            'Zreb_wsk': 'TEMPORARY_OUTPUT'
        }
        self.runRequested.emit(params)
