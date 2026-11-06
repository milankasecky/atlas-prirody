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

## Datová struktura

Každý druh (houba, rostlina, živočich) je jeden JSON soubor v
`data/<skupina>/<id>.json`.

**Společná pole** (houby, rostliny, živočichové):

- `id` – jednoznačný identifikátor (= název souboru bez přípony)
- `skupina` – `houba` / `rostlina` / `zivocich`
- `nazevCesky`, `nazevLatinsky`
- `mesiceVyskytu[]` – měsíce výskytu, hodnoty z číselníku `mesice`
- `stanoviste[]` – typ prostředí, hodnoty z číselníku `stanoviste`
- `popis` – volný text (vzhled, poznání druhu)
- `zamenyS` – volný text (záměny s jinými druhy)
- `fotky[]` – názvy souborů fotek (ve `fotky/<skupina>/`)
- `poznamka` – volný text (vlastní poznámka k nálezu)
- `stitky[]` – volné štítky (text bez omezení, pro cokoliv dalšího)

**Pole jen pro houby:**

- `jedlost` – jedna hodnota z číselníku `jedlost`
- `stromy[]` – mykorhizní stromy, hodnoty z číselníku `stromy`

**Číselníky pevných hodnot** jsou v `data/hodnoty.json` (společný soubor,
lze kdykoliv rozšiřovat o nové hodnoty). Obsahuje:

- `mesice` – 12 měsíců
- `stanoviste` – jehličnatý/listnatý/smíšený les, louka, pole, mokřad,
  u vody, zahrada, park, městská zástavba, hory
- `stromy` (jen houby) – buk, dub, bříza, habr, lípa, topol, olše, smrk,
  borovice, jedle, modřín, ovocné stromy
- `jedlost` (jen houby) – výborná jedlá, jedlá, podmínečně jedlá, léčivá,
  nejedlá, jedovatá, smrtelně jedovatá

Tyto seznamy slouží i pro filtrování (např. „březen + louka + jedlé").
Hodnoty lze přidávat kdykoliv; mazat/přejmenovávat `id` už existující
hodnoty je třeba opatrně – vyžaduje ruční opravu záznamů, které ji používají.

### Adresářová struktura

```
data/
  hodnoty.json          – číselníky povolených hodnot
  houby/*.json          – záznamy hub (1 soubor = 1 druh)
  rostliny/*.json        – záznamy rostlin (zatím prázdné)
  zivocichove/*.json     – záznamy živočichů (zatím prázdné)
fotky/
  houby/                 – fotky k houbám (název = podle pole "fotky")
  rostliny/
  zivocichove/
```

Ukázkový záznam: `data/houby/hrib-smrkovy.json`.

## Stav projektu

- 2026-11-06: Založen git repozitář, `CLAUDE.md`. Dohodnuta a založena
  datová struktura – společná pole pro všechny skupiny + pole jen pro houby,
  číselníky v `data/hodnoty.json`, adresářová struktura `data/` a `fotky/`,
  ukázkový záznam houby (Hřib smrkový). Zatím žádný zobrazovací kód (web
  stránka, PWA).
- **Další krok:** fáze 3 – základní statická stránka, která načte data z
  `data/` a zobrazí seznam hub + detail houby (zatím bez PWA, jen v
  prohlížeči).
