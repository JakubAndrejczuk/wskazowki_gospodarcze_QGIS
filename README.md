# Wskazówki gospodarcze (QGIS Plugin)

Wtyczka QGIS do **wizualizacji wskazówek gospodarczych** dla **cięć rębnych** *(I*, II*, III*, IV* i V*)* oraz **trzebieży** *(TWP i TPP)* zgodnie z obowiązującym **Planem Urządzenia Lasu**, na podstawie danych z **SILP**.

Wtyczka generuje dwie warstwy wynikowe z gotowym stylem (QML), ułatwiające analizę i prezentację wskazówek w QGIS.

---

## Funkcje

- Tworzy warstwę **`zreb_wsk`** – działki zrębowe z:
  - adresem leśnym,
  - rodzajem rębni,
  - powierzchnią manipulacyjną *(pow_man)*.
- Tworzy warstwę **`wydz_wsk`** – wydzielenia leśne z:
  - adresem leśnym,
  - rodzajem trzebieży,
  - powierzchnią manipulacyjną *(pow_man)*,
  - **zasięgiem pomniejszonym o działki zrębowe** leżące w obrębie danego wydzielenia.
- Automatycznie nadaje styl warstwom wynikowym:
  - `Style/wydz_wsk.qml`
  - `Style/zreb_wsk.qml`
- Uruchamianie z poziomu ikony wtyczki: otwiera natywne okno **Processing** (łatwe powtarzanie i parametryzacja).
- Po dodaniu wyników do projektu wtyczka może ustawić widoczność warstw tak, by szybko przejść do analizy (domyślnie „skupia się” na wynikach).

---

## Wymagania

- **QGIS 3.x** (minimum: `3.0` zgodnie z `metadata.txt`)
- Dane wejściowe w strukturze warstw pochodnych **LMN**

---

## Dane wejściowe

Wtyczka korzysta z 3 warstw wejściowych:

1. **`wydz_pol` (pochodne)** – warstwa poligonowa w strukturze LMN  
2. **`zreb_pol` (pochodne)** – warstwa poligonowa w strukturze LMN  
3. **Raport BO ze wskazówkami gospodarczymi** *(formularz BO)* – warstwa/tabela wczytana do QGIS  
   - raport dostępny w BO (SILP) – zgodnie z informacją w opisie wtyczki  
   - **Uwaga:** przed uruchomieniem zapytania raport należy zapisać w folderze osobistym (zgodnie z opisem wtyczki)

---

## Warstwy wynikowe

- **`zreb_wsk`** – działki zrębowe z atrybutami wskazówek
- **`wydz_wsk`** – wydzielenia z atrybutami wskazówek trzebieżowych, z pomniejszeniem o zręby

---

## Instalacja

### Opcja A (dla użytkowników): instalacja z ZIP
1. Pobierz paczkę ZIP wtyczki (np. z zakładki **Releases** na GitHub).
2. W QGIS wybierz: **Wtyczki → Zarządzaj i instaluj wtyczki → Instaluj z pliku ZIP**
3. Wskaż ZIP i zainstaluj.

### Opcja B (dla developerów): sklonowanie repozytorium
Skopiuj katalog wtyczki do profilu QGIS, np.:
- Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
- Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
- macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

---

## Jak używać (krok po kroku)

1. Wczytaj do projektu warstwy:
   - `wydz_pol` (pochodne)
   - `zreb_pol` (pochodne)
   - raport BO ze wskazówkami gospodarczymi (formularz BO)
2. Kliknij ikonę **„Wskazówki gospodarcze”** na pasku narzędzi (lub z menu wtyczek).
3. Otworzy się natywne okno **Processing** z algorytmem wtyczki.
4. Ustaw parametry:
   - **wskazówki gospodarcze (formularz BO)**
   - **wydz_pol (pochodne)**
   - **zreb_pol (pochodne)**
5. Uruchom algorytm.
6. W projekcie pojawią się warstwy wynikowe:
   - `wydz_wsk` (ze stylem)
   - `zreb_wsk` (ze stylem)

---

## Uwagi / ograniczenia

- Wtyczka **nie uwzględnia aktualnego zaawansowania realizacji wskazówek** – generowane są wszystkie wskazówki dla danego 10-lecia na podstawie danych z SILP (zgodnie z opisem).
- Styl warstw wynikowych jest ładowany automatycznie z plików QML w katalogu `Style/`.

---

## Id algorytmu

Algorytm processing ma identyfikator:

- `wtyczka:wskazowki_gospodarcze`

Możesz go też uruchamiać z konsoli/Model Buildera jak standardowy algorytm Processing.

---

## Struktura projektu

W repozytorium znajdują się m.in.:
- `algorithm.py` – logika algorytmu Processing
- `plugin.py` – integracja z interfejsem QGIS (ikona, menu, otwieranie Processing)
- `Style/*.qml` – style dla warstw wynikowych
- `Opis.txt` – opis wyświetlany w panelu pomocy algorytmu

---

## Zgłaszanie błędów

Jeśli coś nie działa, w zgłoszeniu (Issues) podaj proszę:
- wersję QGIS,
- system operacyjny,
- kroki odtworzenia problemu,
- komunikat błędu / traceback (jeśli jest),
- informację o źródle i formacie raportu BO.

---

## Licencja

Zobacz plik: `LICENSE`.

---

## Autor

**Jakub Andrejczuk**  
jakub.andrejczuk@torun.lasy.gov.pl
