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
- `zamenyS` – volný text (čím se liší od zaměnitelných druhů)
- `zamenyId[]` – odkazy (id) na konkrétní záznamy zaměnitelných druhů; v
  detailu se zobrazí jako tlačítko, po kliknutí se pod aktuálním záznamem
  otevře detail té druhé houby (jde zavřít křížkem)
- `fotky[]` – názvy souborů fotek (ve `fotky/<skupina>/`)
- `zaznamyNalezu[]` – vlastní nálezy tohoto druhu, každý jako
  `{ datum, misto, podminky }` (volný text) – stejný druh lze zaznamenat
  vícekrát na různých místech/datech
- `stitky[]` – volné štítky (text bez omezení, pro cokoliv dalšího)

**Pole jen pro houby:**

- `jedlost` – jedna hodnota z číselníku `jedlost`
- `lecive` – `true`/`false`, nezávislé na jedlosti (houba může být jedlá
  i léčivá zároveň)
- `stromy[]` – mykorhizní stromy, hodnoty z číselníku `stromy`
- `testovaciZaznam` – `true` u ukázkových/testovacích záznamů, které se
  později smažou (zatím mají tento příznak všechny houby v `data/houby/`)

**Číselníky pevných hodnot** jsou v `data/hodnoty.json` (společný soubor,
lze kdykoliv rozšiřovat o nové hodnoty). Obsahuje:

- `mesice` – 12 měsíců
- `stanoviste` – jehličnatý/listnatý/smíšený les, louka, pole, mokřad,
  u vody, zahrada, park, městská zástavba, hory
- `stromy` (jen houby) – buk, dub, bříza, habr, lípa, topol, olše, smrk,
  borovice, jedle, modřín, ovocné stromy
- `jedlost` (jen houby) – výborná jedlá, jedlá, podmínečně jedlá,
  nejedlá, jedovatá, smrtelně jedovatá
  (léčivost je samostatné pole `lecive`, ne součást jedlosti)

Tyto seznamy slouží i pro filtrování (např. „březen + louka + jedlé").
Hodnoty lze přidávat kdykoliv; mazat/přejmenovávat `id` už existující
hodnoty je třeba opatrně – vyžaduje ruční opravu záznamů, které ji používají.

### Adresářová struktura

```
index.html               – hlavní stránka (seznam + detail houby)
css/style.css             – vzhled (mobile-first, funguje i na počítači)
js/app.js                 – načtení dat, filtrování, vykreslení

data/
  hodnoty.json            – číselníky povolených hodnot
  houby/index.json        – seznam id souborů hub, které se mají načíst
  houby/*.json            – záznamy hub (1 soubor = 1 druh)
  rostliny/*.json         – záznamy rostlin (zatím prázdné)
  zivocichove/*.json      – záznamy živočichů (zatím prázdné)
fotky/
  houby/                  – fotky k houbám (název = podle pole "fotky")
  rostliny/
  zivocichove/
```

Důležité: když přidáš nový soubor `data/houby/<id>.json`, musíš jeho `id`
přidat i do `data/houby/index.json`, jinak se v aplikaci nezobrazí.

V `data/houby/` je zatím 5 **testovacích** záznamů (Hřib smrkový, Muchomůrka
červená, Liška obecná, Žampion polní, Pýchavka obecná) – mají příznak
`"testovaciZaznam": true` a v aplikaci jsou označeny štítkem "TESTOVACÍ
ZÁZNAM". Slouží jen k vyzkoušení filtrování, později se smažou a nahradí
skutečnými daty.

## Stav projektu

- 2026-11-06: Založen git repozitář, `CLAUDE.md`, datová struktura
  (číselníky, společná/houbí pole, adresáře `data/` a `fotky/`). Vytvořena
  fáze 3 – funkční statická webová stránka (`index.html`, `css/style.css`,
  `js/app.js`): seznam hub, detail s fotkami a textem, filtry podle měsíce,
  stanoviště, stromu a jedlosti, checkbox "jen léčivé", hledání podle názvu.
  Vzhled mobile-first, funguje i na počítači. Doplněno 5 testovacích záznamů
  hub pro vyzkoušení filtrů (viz výše). Ověřeno přes lokální server
  (`python -m http.server`), že se stránka a data správně načtou. Zatím bez
  PWA/offline režimu a bez nasazení na GitHub Pages.
- 2026-11-06: Doplněn oddíl "Záznam nálezu" (pole `zaznamyNalezu[]` –
  vlastní nálezy s datem/místem/podmínkami, nahradilo pole `poznamka`) a
  propojení záměn mezi záznamy (`zamenyId[]`) – v detailu houby lze
  kliknutím na odkaz otevřít detail zaměnitelného druhu přímo pod aktuálním
  záznamem, se zavřením křížkem. Otestováno přes lokální server.
- **Další krok:** fáze 4 (rozšíření vyhledávání/filtrů) je už z větší části
  hotová společně s fází 3 – zbývá fáze 5 (reálné zpracování fotek: zmenšení
  + odstranění GPS/EXIF) a fáze 6 (PWA – manifest, ikony, Service Worker,
  offline režim). Uživatel ještě musí doplnit vlastní fotky a reálné houby
  namísto testovacích záznamů.
