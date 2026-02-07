# -*- coding: utf-8 -*-
import os
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterFeatureSink,
    QgsProcessingOutputLayerDefinition,
    QgsProcessingContext,
    QgsProcessingParameterBoolean,
)
import processing

class WskazowkiGospodarczeAlg(QgsProcessingAlgorithm):
    """
    Id: 'wtyczka:wskazowki_gospodarcze'
    """

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(
            'wskazwki_gospodarcze_fromularz_bo',
            'wskazówki gospodarcze (fromularz BO)',
            types=[QgsProcessing.TypeVector],
            defaultValue=None
        ))
        self.addParameter(QgsProcessingParameterVectorLayer(
            'wydz_pol_pochodne',
            'wydz_pol (pochodne)',
            types=[QgsProcessing.TypeVectorPolygon],
            defaultValue=None
        ))
        self.addParameter(QgsProcessingParameterVectorLayer(
            'zreb_pol_pochodne',
            'zreb_pol (pochodne)',
            types=[QgsProcessing.TypeVectorPolygon],
            defaultValue=None
        ))

        # Opcja dialogowa: wizualizacja wykonania wskazówek
        self.addParameter(QgsProcessingParameterBoolean(
            'wizualizacja_wykonania_wskazowek',
            'Wizualizacja wykonania wskazówek',
            defaultValue=False
        ))

        # Wyjścia – podpisy odpowiadają nazwom docelowym
        self.addParameter(QgsProcessingParameterFeatureSink(
            'Wydz_wsk', 'wydz_wsk',
            type=QgsProcessing.TypeVectorAnyGeometry,
            createByDefault=True,
            defaultValue=None
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            'Zreb_wsk', 'zreb_wsk',
            type=QgsProcessing.TypeVectorAnyGeometry,
            createByDefault=True,
            supportsAppend=True,
            defaultValue=None
        ))

    def shortHelpString(self):
        """
        Tekst w prawym panelu natywnego okna Processing.
        Wczytywany z Opis.txt znajdującego się w folderze wtyczki.
        """
        plugin_dir = os.path.dirname(__file__)
        opis_path = os.path.join(plugin_dir, 'Opis.txt')
        try:
            with open(opis_path, 'r', encoding='utf-8') as f:
                txt = f.read()
        except Exception:
            txt = 'Brak opisu (plik "Opis.txt" w folderze wtyczki).'
        return txt

    def _ensure_named_temporary_outputs(self, parameters):
        """
        Jeśli użytkownik zostawi wyjścia jako TEMPORARY_OUTPUT,
        wymuś nazwy warstw tymczasowych: 'wydz_wsk' i 'zreb_wsk'.
        """
        if (parameters.get('Wydz_wsk') in (None, QgsProcessing.TEMPORARY_OUTPUT, 'TEMPORARY_OUTPUT')):
            parameters['Wydz_wsk'] = QgsProcessingOutputLayerDefinition(
                QgsProcessing.TEMPORARY_OUTPUT, 'wydz_wsk'
            )
        if (parameters.get('Zreb_wsk') in (None, QgsProcessing.TEMPORARY_OUTPUT, 'TEMPORARY_OUTPUT')):
            parameters['Zreb_wsk'] = QgsProcessingOutputLayerDefinition(
                QgsProcessing.TEMPORARY_OUTPUT, 'zreb_wsk'
            )

    def _register_names_for_autoload(self, context: QgsProcessingContext, results: dict):
        """
        Jeśli Processing ma automatycznie wczytać warstwy do projektu, ustaw mu nazwę docelową.
        """
        try:
            if 'Wydz_wsk' in results and results['Wydz_wsk']:
                details_w = QgsProcessingContext.LayerDetails('wydz_wsk', context.project(), '')
                context.addLayerToLoadOnCompletion(results['Wydz_wsk'], details_w)
            if 'Zreb_wsk' in results and results['Zreb_wsk']:
                details_z = QgsProcessingContext.LayerDetails('zreb_wsk', context.project(), '')
                context.addLayerToLoadOnCompletion(results['Zreb_wsk'], details_z)
        except Exception:
            pass  # plugin i tak poprawi nazwy w razie potrzeby

    def processAlgorithm(self, parameters, context, model_feedback):
        # Wymuś nazwy, jeśli wyjścia są tymczasowe
        self._ensure_named_temporary_outputs(parameters)

        feedback = QgsProcessingMultiStepFeedback(20, model_feedback)
        results = {}
        outputs = {}

        # 0. Ustaw kodowanie wydz_pol
        alg_params = {
            'ENCODING': 'windows-1250',
            'INPUT': parameters['wydz_pol_pochodne']
        }
        outputs['UstawKodowanieWydz_pol'] = processing.run(
            'native:setlayerencoding', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 1. Napraw geometrie zreb_pol
        alg_params = {
            'INPUT': parameters['zreb_pol_pochodne'],
            'METHOD': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NaprawGeometrieZreb_pol'] = processing.run(
            'native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 2. Zaokrąglij pow_man
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'pow_man',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,
            'FORMULA': 'round("pow_man",2)',
            'INPUT': parameters['wskazwki_gospodarcze_fromularz_bo'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZaokraglijPow_man'] = processing.run(
            'native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 3. Zmień pola formularza
        alg_params = {
            'FIELDS_MAPPING': [
                {'alias': '','comment': '','expression': '"nr_wew"','length': 10,'name': 'nr_wew','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},
                {'alias': '','comment': '','expression': '"adr_les"','length': 25,'name': 'adr_les','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                {'alias': '','comment': '','expression': '"nr_dzialki"','length': 2,'name': 'nr_dzialki','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},
                {'alias': '','comment': '','expression': '"gr_czyn"','length': 10,'name': 'gr_czyn','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                {'alias': '','comment': '','expression': '"pow_man"','length': 10,'name': 'pow_man','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}
            ],
            'INPUT': parameters['wskazwki_gospodarcze_fromularz_bo'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorForm'] = processing.run(
            'native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 4. Trim gr_czyn
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'gr_czyn',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': 'trim("gr_czyn")',
            'INPUT': outputs['ZaokraglijPow_man']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TrimGr_czyn'] = processing.run(
            'native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 5. Napraw geometrie wydz_pol
        alg_params = {
            'INPUT': outputs['UstawKodowanieWydz_pol']['OUTPUT'],
            'METHOD': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NaprawGeometrieWydz_pol'] = processing.run(
            'native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 6. Oblicz adreso_dz w formularzu
        alg_params = {
            'FIELD_LENGTH': 40,
            'FIELD_NAME': 'adreso_dz',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': '"adr_les" || \'_\' || trim("gr_czyn") || \'_\' || "nr_dzialki"',
            'INPUT': outputs['TrimGr_czyn']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdresoForm'] = processing.run(
            'native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 7. wydz bez zrębów
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['NaprawGeometrieWydz_pol']['OUTPUT'],
            'OVERLAY': outputs['NaprawGeometrieZreb_pol']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WydzBezZrebow'] = processing.run(
            'native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # 8. Dodaj adr_les do zreb_pol
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['NaprawGeometrieZreb_pol']['OUTPUT'],
            'JOIN': outputs['NaprawGeometrieWydz_pol']['OUTPUT'],
            'JOIN_FIELDS': ['adr_les'],
            'METHOD': 2,
            'PREDICATE': [0, 4, 5],
            'PREFIX': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAdrLesToZreb'] = processing.run(
            'native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # 9. Wyodrębnij TWP, TPP
        alg_params = {
            'EXPRESSION': '"gr_czyn" IN (\'TWP\', \'TPP\')',
            'INPUT': outputs['AdresoForm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['OnlyTwpTpp'] = processing.run(
            'native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # 10. Oblicz adreso_dz w zreb_pol
        alg_params = {
            'FIELD_LENGTH': 40,
            'FIELD_NAME': 'adreso_dz',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': '"adr_les" || \'_\' || "kod_reb" || \'_\' || "nr_dz"',
            'INPUT': outputs['JoinAdrLesToZreb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AdresoZreb'] = processing.run(
            'native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # 11. Dodaj TWP,TPP  (kopiujemy także 'wyk')
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'adr_les',
            'FIELDS_TO_COPY': ['gr_czyn', 'pow_man', 'wyk'],
            'FIELD_2': 'adr_les',
            'INPUT': outputs['WydzBezZrebow']['OUTPUT'],
            'INPUT_2': outputs['OnlyTwpTpp']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinTwpTpp'] = processing.run(
            'native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # 12. Wyodrębnij wydz z wskazowka
        alg_params = {
            'FIELD': 'gr_czyn',
            'INPUT': outputs['JoinTwpTpp']['OUTPUT'],
            'OPERATOR': 9,
            'VALUE': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WydzZWskazowka'] = processing.run(
            'native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # 13. Wyodrębnij tylko D-STAN
        alg_params = {
            'FIELD': 'rodz_pow',
            'INPUT': outputs['WydzZWskazowka']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': 'D-STAN',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['OnlyDStan'] = processing.run(
            'native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # 14. Dodaj pow_man do zreb  (kopiujemy także 'wyk')
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'adreso_dz',
            'FIELDS_TO_COPY': ['pow_man', 'wyk'],
            'FIELD_2': 'adreso_dz',
            'INPUT': outputs['AdresoZreb']['OUTPUT'],
            'INPUT_2': outputs['AdresoForm']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinPowToZreb'] = processing.run(
            'native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # 15. Oblicz pow geom
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'area',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,
            'FORMULA': '$area',
            'INPUT': outputs['OnlyDStan']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcArea'] = processing.run(
            'native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # 16. Wyodrębnij o pow > 0 -> Wydz_wsk
        alg_params = {
            'FIELD': 'area',
            'INPUT': outputs['CalcArea']['OUTPUT'],
            'OPERATOR': 2,
            'VALUE': 0,
            'OUTPUT': parameters['Wydz_wsk']
        }
        outputs['WydzOut'] = processing.run(
            'native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        results['Wydz_wsk'] = outputs['WydzOut']['OUTPUT']

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # 17. Zmień pola formularza zreb_wsk -> Zreb_wsk (DODANO 'wyk')
        # Używam typu tekstowego dla maksymalnej kompatybilności niezależnie od typu źródłowego.
        alg_params = {
            'FIELDS_MAPPING': [
                {'alias': '','comment': '','expression': '"id_ob"','length': 9,'name': 'id_ob','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},
                {'alias': '','comment': '','expression': '"id_adres"','length': 10,'name': 'id_adres','precision': 0,'sub_type': 0,'type': 4,'type_name': 'int8'},
                {'alias': '','comment': '','expression': '"adr_les"','length': 25,'name': 'adr_les','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                {'alias': '','comment': '','expression': '"nr_dz"','length': 2,'name': 'nr_dz','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},
                {'alias': '','comment': '','expression': '"kod_reb"','length': 9,'name': 'kod_reb','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},
                {'alias': '','comment': '','expression': '"pow_man"','length': 10,'name': 'pow_man','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},
                # nowy atrybut w wyjściu:
                {'alias': '','comment': '','expression': '"wyk"','length': 10,'name': 'wyk','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}
            ],
            'INPUT': outputs['JoinPowToZreb']['OUTPUT'],
            'OUTPUT': parameters['Zreb_wsk']
        }
        outputs['ZrebOut'] = processing.run(
            'native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True
        )
        results['Zreb_wsk'] = outputs['ZrebOut']['OUTPUT']

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # 18–19. (opcjonalne) style z QML
        # wybór stylu zależny od parametru 'wizualizacja_wykonania_wskazowek'
        use_visual = bool(parameters.get('wizualizacja_wykonania_wskazowek', False))
        style_dir = os.path.join(os.path.dirname(__file__), 'Style')
        wydz_fname = 'wydz_wsk_wyk.qml' if use_visual else 'wydz_wsk.qml'
        zreb_fname = 'zreb_wsk_wyk.qml' if use_visual else 'zreb_wsk.qml'

        wydz_style = os.path.join(style_dir, wydz_fname)
        if os.path.exists(wydz_style):
            processing.run(
                'native:setlayerstyle',
                {'INPUT': outputs['WydzOut']['OUTPUT'], 'STYLE': wydz_style},
                context=context, feedback=feedback, is_child_algorithm=True
            )
        zreb_style = os.path.join(style_dir, zreb_fname)
        if os.path.exists(zreb_style):
            processing.run(
                'native:setlayerstyle',
                {'INPUT': outputs['ZrebOut']['OUTPUT'], 'STYLE': zreb_style},
                context=context, feedback=feedback, is_child_algorithm=True
            )

        # 20) Zarejestruj nazwy do autoload (gdy Processing doda warstwy do projektu)
        self._register_names_for_autoload(context, results)

        return results

    def name(self):
        return 'wskazowki_gospodarcze'

    def displayName(self):
        return 'Wskazówki gospodarcze'

    def group(self):
        return 'LMN'

    def groupId(self):
        return 'LMN'

    def createInstance(self):
        return WskazowkiGospodarczeAlg()
