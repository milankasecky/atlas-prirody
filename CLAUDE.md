# Atlas přírody

Osobní offline encyklopedie přírody pro mobil. Začínáme houbami, později
přibudou rostliny a živočichové.

## Cíle a požadavky

- Jednoduchá webová aplikace – čisté HTML, CSS, JavaScript. Žádné sestavovací
  nástroje (bez Reactu, bundlerů apod.), aby bylo vše pochopitelné i pro
  začátečníka.
- Instalovatelná na Android jako PWA (ikona na ploše) a plně funkční bez
  internetu – včetně všech fotek (offline cache přes Service Worker).
- Data (texty a fotky) doplňuje uživatel sám, uložená v přehledných souborech
  v tomto repozitáři (např. JSON pro texty, složky s obrázky).
- Datová struktura je od začátku připravena na tři kategorie: houby,
  rostliny, živočichové – i když zatím existují jen houby.
- Fotky se před zařazením do aplikace zmenší a zbaví se EXIF/GPS metadat
  (kvůli velikosti i soukromí).
- Nasazení zdarma přes GitHub Pages.
- Veškerý text v aplikaci i komentáře v kódu jsou v češtině.

## Pravidla spolupráce

- Vysvětluj stručně, jen to klíčové – uživatel je v programování úplný
  začátečník.
- Před velkými změnami se nejdřív zeptej a popiš, co se chystáš udělat.
- Po každé funkční části ulož verzi do gitu (commit), aby bylo možné se
  kdykoliv vrátit k fungujícímu stavu.
- Na konci každého sezení zapiš do tohoto souboru (sekce "Stav projektu"
  níže), kde jsme skončili a jaký je další krok.

## Plán po fázích

1. **Příprava** – git repozitář, CLAUDE.md, dohoda na datové struktuře houby
   (jaké údaje se budou evidovat).
2. **Datový základ** – adresářová struktura pro data a fotky, ukázková data
   pro pár hub.
3. **Základní zobrazení** – statická stránka, která načte data a zobrazí
   seznam hub + detail houby (bez PWA, jen v prohlížeči).
4. **Vyhledávání a filtrování** – podle názvu, případně dalších znaků.
5. **Zpracování fotek** – skript/postup na zmenšení fotek a odstranění GPS
   / EXIF dat před vložením do aplikace.
6. **PWA a offline režim** – manifest, ikony, Service Worker pro offline
   fungování včetně fotek, instalace na Android.
7. **Nasazení** – zveřejnění přes GitHub Pages.
8. **Rozšíření** – příprava a doplnění kategorií rostliny a živočichové.

## Stav projektu

- 2026-11-06: Založen git repozitář, vytvořen tento CLAUDE.md. Zatím žádný
  kód. Dohodnutá datová struktura pro houby: *(doplní se po rozhovoru s
  uživatelem)*.
- **Další krok:** domluvit s uživatelem, jaké údaje se budou u houby
  evidovat, pak založit adresářovou strukturu dat (fáze 2).
