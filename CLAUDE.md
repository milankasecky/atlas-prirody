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
- `fotky[]` – základy názvů fotek (bez přípony, bez velikosti), např.
  `"hrib-smrkovy-1"`. Ke každému existují v `fotky/<skupina>/` dva
  soubory: `<zaklad>-mala.jpg` (náhled) a `<zaklad>-velka.jpg` (detail).
  Vznikají automaticky skriptem – viz "Zpracování fotek" níže.
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
  houby/                  – zpracované fotky (<zaklad>-mala.jpg / -velka.jpg)
  rostliny/
  zivocichove/

nastroje/
  zpracuj_fotky.py        – zmenší fotky, odstraní metadata, viz níže

nove-fotky/<id>/           – SEM vkládáš originály (mimo git, viz .gitignore)
archiv-fotky/<id>/         – originály po zpracování (mimo git)
```

Důležité: když přidáš nový soubor `data/houby/<id>.json`, musíš jeho `id`
přidat i do `data/houby/index.json`, jinak se v aplikaci nezobrazí.

V `data/houby/` je zatím 5 **testovacích** záznamů (Hřib smrkový, Muchomůrka
červená, Liška obecná, Žampion polní, Pýchavka obecná) – mají příznak
`"testovaciZaznam": true` a v aplikaci jsou označeny štítkem "TESTOVACÍ
ZÁZNAM". Slouží jen k vyzkoušení filtrování, později se smažou a nahradí
skutečnými daty.

## Zpracování fotek

Originální fotky (rovnou z mobilu) se **nikdy** nenahrávají do gitu – mají
GPS polohu a jsou velké. Postup:

1. Originály vlož do `nove-fotky/<id-druhu>/` (složku si vytvoř, pokud
   neexistuje – jméno musí přesně odpovídat `id` druhu, např.
   `nove-fotky/hrib-smrkovy/`).
2. Spusť (nebo požádej mě, ať to udělám za tebe větou typu "zpracuj nové
   fotky pro hřib smrkový"):
   ```
   python nastroje/zpracuj_fotky.py hrib-smrkovy
   ```
3. Skript pro každou fotku:
   - zmenší ji na dvě verze (malá pro seznam, velká pro detail),
   - odstraní VŠECHNA metadata (EXIF), včetně GPS,
   - ověří, že výsledné soubory opravdu žádná metadata neobsahují,
   - až po úspěšném ověření přesune originál do `archiv-fotky/<id-druhu>/`
     (neslaže ho) a doplní nové fotky do pole `fotky` v
     `data/houby/<id-druhu>.json`.
4. Pokud ověření selže, skript originály nepřesune a JSON neupraví –
   vypíše, co je špatně.
5. Teprve po úspěšném zpracování se nové fotky a upravený JSON uloží do
   gitu (běžným commitem).

Složky `nove-fotky/` a `archiv-fotky/` jsou v `.gitignore` – existují jen
lokálně na tomto počítači, po novém klonování repozitáře je třeba je
znovu vytvořit.

## Nové záznamy přes textové karty

Nové houby se zapisují na PC jako obyčejné textové karty (řádky
`Pole: hodnota`), převod do aplikace dělá skript
`nastroje/zpracuj_zaznamy.py` – pokaždé stejně.

1. Vzor karty: `nove-zaznamy/_vzor-karty-houby.txt` (kopie i v
   `nastroje/vzor-karty-houby.txt`). Obsahuje nápovědu s povolenými
   hodnotami z `data/hodnoty.json`; skript ho při každém spuštění
   přegeneruje, takže je vždy aktuální.
2. Vyplněná karta = `nove-zaznamy/<id>.txt`, fotky do
   `nove-fotky/<id>/` (stejný název).
3. Pole `Soukromé:` (lokality, osobní poznámky) se do aplikace NIKDY
   nepřevádí. `Nález místo` je naopak veřejné.
4. Na pokyn **„zpracuj nové záznamy"** spusť:
   ```
   python nastroje/zpracuj_zaznamy.py
   ```
   (`--kontrola` = jen kontrola bez ukládání). Skript nejdřív
   zkontroluje všechny karty; při jakékoliv chybě (hodnota mimo
   číselník, překlep v poli, špatné datum, neplatný název souboru…)
   neuloží NIC a vypíše, co opravit – tyto chyby předej uživateli.
   Když je vše OK: zpracuje fotky (zmenšení, odstranění EXIF/GPS,
   ověření), uloží `data/houby/<id>.json`, doplní `index.json`, originály
   přesune do `archiv-fotky/<id>/` a karty do `archiv-zaznamy/`.
5. Karta se stejným id jako testovací záznam ho nahradí (zachová jeho
   fotky); skutečný existující záznam skript nepřepíše.
6. Po úspěšném převodu změny commitni; nahrání na GitHub (push) jen po
   souhlasu uživatele.

Složky `nove-zaznamy/` a `archiv-zaznamy/` jsou v `.gitignore`.

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
- 2026-11-06: Fáze 6 (základ PWA) – přidán `manifest.json`, ikony
  `icons/icon-192.png` a `icons/icon-512.png` (vygenerované jednoduchým
  skriptem, jen placeholder – půjde později nahradit vlastní grafikou),
  `sw.js` (service worker se strategií "nejdřív síť, při výpadku cache").
  V `js/app.js` přidána registrace service workeru a funkce
  `ulozVseProOffline()`, která při každém spuštění s internetem doplní do
  cache úplně všechna data i fotky (i nově přidané), aby šly použít i bez
  internetu při příštím otevření. Ověřeno, že se manifest/ikony/sw.js
  správně načtou přes lokální server; samotnou instalaci do mobilu a chod
  bez internetu je nutné ověřit v reálném prohlížeči (nelze otestovat jen
  příkazovou řádkou).
- 2026-11-06: Založen veřejný GitHub repozitář `milankasecky/atlas-prirody`,
  zapnuty GitHub Pages (větev `main`, root). Appka běží na
  https://milankasecky.github.io/atlas-prirody/ – ověřeno nasazení (všechny
  soubory dostupné) i uživatelem přímo na mobilu: instalace přes "Přidat na
  plochu" a chod úplně bez internetu (režim letadlo) funguje, včetně PWA
  cache dat a fotek.
- 2026-11-06: Fáze 5 hotová a odzkoušená na reálné fotce z mobilu – nástroj
  `nastroje/zpracuj_fotky.py` zmenšil fotku Hřibu smrkového na dvě verze,
  odstranil EXIF/GPS metadata, ověřil (0 EXIF položek, bez GPS), přesunul
  originál do `archiv-fotky/` a doplnil `data/houby/hrib-smrkovy.json`.
  Zpracovaná fotka uložena do gitu a nahrána na GitHub Pages.
- 2026-11-06: Doplněno zvětšení fotky na celou obrazovku (lightbox) po
  kliknutí v detailu houby – ověřeno uživatelem na mobilu, funguje. Ověřeno
  i automatické zaktualizování appky na mobilu (díky strategii "nejdřív
  síť" stačí appku znovu otevřít s internetem, bez přeinstalace).
- 2026-11-06: Přidány textové karty hub a skript
  `nastroje/zpracuj_zaznamy.py` (viz oddíl "Nové záznamy přes textové
  karty"). Otestováno na kopii projektu: chybné karty se neuloží, pole
  Soukromé se nepřevádí, fotky bez GPS, karty se archivují.
- **Další krok:** uživatel bude postupně doplňovat vlastní reálné houby a
  fotky (přes `nastroje/zpracuj_fotky.py`) a nahrazovat jimi testovací
  záznamy. Až bude dost reálných dat, smazat testovací záznamy
  (`"testovaciZaznam": true`) a případně začít s rostlinami/živočichy.
