# Wskazówki gospodarcze (QGIS Plugin)

Wtyczka QGIS do generowania i wizualizacji **wskazówek gospodarczych** dla cięć rębnych i trzebieży na podstawie danych SILP oraz raportu BO.

## Przeznaczenie

Wtyczka dedykowana dla pracowników **Lasów Państwowych**.  
Umożliwia przygotowanie warstw przestrzennych prezentujących wskazówki gospodarcze zgodnie z Planem Urządzenia Lasu.

Generowane są warstwy przedstawiające:
- cięcia rębne (I*, II*, III*, IV*, V*),
- trzebieże (TWP i TPP).

---

## Wymagania

- **QGIS:** 3.0 lub nowszy,
- **warstwy LMN (pochodne):**
  - `wydz_pol`,
  - `zreb_pol`,
- **raport BO** ze wskazówkami gospodarczymi (zapisany w folderze osobistym użytkownika),
- dostęp do środowiska i danych **SILP**.

---

## Wejście i wyjście

### Dane wejściowe

1. **wydz_pol (pochodne)** – warstwa wydzieleń leśnych.  
2. **zreb_pol (pochodne)** – warstwa działek zrębowych.  
3. **Raport BO** – raport ze wskazówkami gospodarczymi.

### Dane wynikowe

- **`zreb_wsk`** – działki zrębowe z przypisanym adresem leśnym, rodzajem rębni oraz powierzchnią manipulacyjną,  
- **`wydz_wsk`** – wydzielenia leśne z przypisanymi:
  - adresem leśnym,
  - rodzajem trzebieży,
  - powierzchnią manipulacyjną,  
  zasięg wydzieleń pomniejszony o działki zrębowe w obrębie obiektu.

---

## Funkcjonalność

Algorytm przetwarza dane wejściowe i generuje warstwy wynikowe w oparciu o operacje Processing QGIS, m.in.:

- naprawa geometrii warstw,
- refaktoryzacja pól formularza,
- łączenie atrybutów i analizę przestrzenną,
- obliczanie powierzchni manipulacyjnych,
- generowanie warstw wynikowych `wydz_wsk` i `zreb_wsk`.

---

## Wizualizacja wykonania wskazówek

Opcja **„Wizualizacja wykonania wskazówek”**:

- nadaje styl warstwom wynikowym,
- rozróżnia pozycje wykonane i niewykonane (wg stanu na poprzedni rok),
- w przypadku zmiany rodzaju wykonanej rębni – prezentuje stan faktyczny, z kodem wskazówki w nawiasie.

---

## Instalacja

1. Pobierz paczkę ZIP wtyczki (np. z GitHub).
2. W QGIS wybierz: **Wtyczki → Zarządzaj i instaluj wtyczki → Instaluj z pliku ZIP**
3. Wskaż plik ZIP i zainstaluj wtyczkę.

---

## Podstawowy workflow

1. Przygotuj warstwy `wydz_pol` i `zreb_pol` (pochodne LMN).
2. Pobierz i zapisz raport BO w folderze osobistym użytkownika.
3. Uruchom wtyczkę.
4. Wskaż dane wejściowe.
5. Uruchom algorytm.
6. Otrzymaj warstwy wynikowe:
   - `wydz_wsk`,
   - `zreb_wsk`.

---

## Ograniczenia i uwagi

- Wtyczka została zaprojektowana dla struktury danych **LMN i SILP**.
- Poprawność działania zależy od jakości danych wejściowych i zgodności ich struktury.
- Zalecane jest korzystanie z aktualnych raportów BO.

---

## Autor i kontakt

- **Autor:** Jakub Andrejczuk  
- **E-mail:** jakub.andrejczuk@torun.lasy.gov.pl  

Instrukcja wideo: https://youtu.be/Gj33hPJq5nU
