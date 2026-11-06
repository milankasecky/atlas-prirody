"""
Zpracování nových fotek pro jeden druh (houba/rostlina/živočich).

Použití:
    python nastroje/zpracuj_fotky.py <id-druhu>

Co skript udělá:
  1. Najde originály v nove-fotky/<id-druhu>/
  2. Z každé fotky vytvoří dvě zmenšené verze (malá pro seznam, velká pro
     detail) bez jakýchkoliv skrytých metadat (EXIF, GPS...) a uloží je do
     fotky/<skupina>/
  3. Ověří, že ve výsledných fotkách opravdu není žádná poloha (GPS) ani
     jiné EXIF údaje.
  4. Teprve když je ověření v pořádku, přesune originály do
     archiv-fotky/<id-druhu>/ (nemaže je) a doplní nové fotky do seznamu
     "fotky" v data/<skupina>/<id-druhu>.json.

Složky nove-fotky/ a archiv-fotky/ se nikdy nenahrávají do gitu
(viz .gitignore) – obsahují originály, které mohou mít GPS polohu.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

# Vynutit UTF-8 výstup do terminálu (na Windows by jinak česká diakritika
# ve výpisu mohla být nečitelná podle nastavení konzole).
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

KOREN = Path(__file__).resolve().parent.parent

MALA_MAX_PX = 400       # max. rozměr pro náhled v seznamu
VELKA_MAX_PX = 1600     # max. rozměr pro zobrazení v detailu
KVALITA_MALA = 78
KVALITA_VELKA = 85

PRIPONY_OBRAZKU = {".jpg", ".jpeg", ".png"}


def najdi_zaznam_druhu(id_druhu):
    """Najde JSON soubor druhu v data/houby|rostliny|zivocichove/<id>.json."""
    for skupina_slozka in ("houby", "rostliny", "zivocichove"):
        cesta = KOREN / "data" / skupina_slozka / f"{id_druhu}.json"
        if cesta.exists():
            return skupina_slozka, cesta
    return None, None


def zmenseny_obrazek(obrazek, max_rozmer):
    """Vrátí kopii obrázku zmenšenou tak, aby delší strana nebyla větší než max_rozmer."""
    kopie = obrazek.copy()
    kopie.thumbnail((max_rozmer, max_rozmer), Image.LANCZOS)
    return kopie


def uloz_bez_metadat(obrazek, cesta, kvalita):
    """Uloží obrázek jako JPEG BEZ jakýchkoliv EXIF/GPS metadat."""
    if obrazek.mode != "RGB":
        obrazek = obrazek.convert("RGB")
    # Záměrně se nepředává parametr exif= -> ve výstupním souboru nebudou
    # žádná metadata (žádná poloha, žádný čas, žádný model telefonu...).
    obrazek.save(cesta, format="JPEG", quality=kvalita, optimize=True)


def ma_soubor_exif_nebo_gps(cesta):
    """Ověří výsledný soubor: vrátí (ma_jakekoliv_exif, ma_gps)."""
    with Image.open(cesta) as obrazek:
        exif = obrazek.getexif()
        ma_exif = len(exif) > 0
        # Tag 0x8825 = GPSInfo
        ma_gps = 0x8825 in exif
        return ma_exif, ma_gps


def najdi_dalsi_volne_cislo(slozka_fotek, id_druhu):
    """Zjistí nejvyšší už použité pořadové číslo fotky daného druhu."""
    nejvyssi = 0
    if slozka_fotek.exists():
        for soubor in slozka_fotek.glob(f"{id_druhu}-*-mala.jpg"):
            try:
                cislo = int(soubor.stem.split("-")[-2])
                nejvyssi = max(nejvyssi, cislo)
            except (ValueError, IndexError):
                continue
    return nejvyssi + 1


def zpracuj(id_druhu):
    slozka_novych = KOREN / "nove-fotky" / id_druhu

    if not slozka_novych.exists():
        print(f"Složka {slozka_novych} neexistuje – není co zpracovat.")
        print(f"Vytvoř ji a vlož do ní fotky druhu '{id_druhu}'.")
        return 1

    soubory = sorted(
        p for p in slozka_novych.iterdir()
        if p.suffix.lower() in PRIPONY_OBRAZKU
    )
    if not soubory:
        print(f"Ve složce {slozka_novych} nejsou žádné fotky (.jpg/.jpeg/.png).")
        return 1

    skupina, cesta_json = najdi_zaznam_druhu(id_druhu)
    if not cesta_json:
        print(f"Nenašel jsem záznam '{id_druhu}' v data/houby|rostliny|zivocichove/.")
        print("Nejdřív vytvoř JSON záznam druhu, pak teprve zpracovávej fotky.")
        return 1

    slozka_fotek = KOREN / "fotky" / skupina
    slozka_fotek.mkdir(parents=True, exist_ok=True)
    cislo = najdi_dalsi_volne_cislo(slozka_fotek, id_druhu)

    print(f"Druh: {id_druhu}  (skupina: {skupina})")
    print(f"Nalezeno originálů: {len(soubory)}")
    print()

    vytvorene = []  # dvojice (zaklad_nazvu, cesta_mala, cesta_velka, original)

    for original in soubory:
        zaklad = f"{id_druhu}-{cislo}"
        cesta_mala = slozka_fotek / f"{zaklad}-mala.jpg"
        cesta_velka = slozka_fotek / f"{zaklad}-velka.jpg"

        with Image.open(original) as obrazek:
            # Natočení podle EXIF orientace se musí "zapéct" do pixelů
            # předtím, než metadata zahodíme – jinak by fotka mohla
            # vyjít na výšku/na šířku špatně.
            obrazek = ImageOps.exif_transpose(obrazek)

            uloz_bez_metadat(zmenseny_obrazek(obrazek, MALA_MAX_PX), cesta_mala, KVALITA_MALA)
            uloz_bez_metadat(zmenseny_obrazek(obrazek, VELKA_MAX_PX), cesta_velka, KVALITA_VELKA)

        print(f"  {original.name} -> {cesta_mala.name}, {cesta_velka.name}")
        vytvorene.append((zaklad, cesta_mala, cesta_velka, original))
        cislo += 1

    # ---- Ověření, že výsledné fotky opravdu neobsahují GPS ani jiná EXIF data ----
    print()
    print("Ověřuji metadata výsledných fotek...")
    vse_v_poradku = True
    for zaklad, cesta_mala, cesta_velka, _ in vytvorene:
        for cesta in (cesta_mala, cesta_velka):
            ma_exif, ma_gps = ma_soubor_exif_nebo_gps(cesta)
            stav = "OK" if not ma_exif and not ma_gps else "CHYBA"
            print(f"  [{stav}] {cesta.name} – EXIF: {'ano' if ma_exif else 'ne'}, GPS: {'ano' if ma_gps else 'ne'}")
            if ma_exif or ma_gps:
                vse_v_poradku = False

    if not vse_v_poradku:
        print()
        print("POZOR: některé fotky stále obsahují metadata! Originály se")
        print("NEPŘESOUVAJÍ do archivu a JSON záznam se NEAKTUALIZUJE.")
        print("Zpracované soubory raději smaž a problém nahlas.")
        return 2

    print("Ověřeno – žádná z fotek neobsahuje GPS ani jiná metadata.")
    print()

    # ---- Přesun originálů do archivu (ne smazání) ----
    slozka_archivu = KOREN / "archiv-fotky" / id_druhu
    slozka_archivu.mkdir(parents=True, exist_ok=True)
    for _, _, _, original in vytvorene:
        cil = slozka_archivu / original.name
        if cil.exists():
            cil = slozka_archivu / f"{original.stem}-{original.stat().st_mtime_ns}{original.suffix}"
        original.replace(cil)
        print(f"  Originál přesunut do archivu: {cil.relative_to(KOREN)}")

    # ---- Doplnění nových fotek do JSON záznamu druhu ----
    data_druhu = json.loads(cesta_json.read_text(encoding="utf-8"))
    fotky_existujici = data_druhu.get("fotky", [])
    nove_zaklady = [zaklad for zaklad, *_ in vytvorene if zaklad not in fotky_existujici]
    data_druhu["fotky"] = fotky_existujici + nove_zaklady
    cesta_json.write_text(
        json.dumps(data_druhu, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print()
    print(f"Záznam {cesta_json.relative_to(KOREN)} aktualizován, pole 'fotky': {data_druhu['fotky']}")

    print()
    print(f"Hotovo. Zpracováno {len(vytvorene)} fotek pro '{id_druhu}'.")
    print("Teď je bezpečné uložit nové fotky i upravený záznam do gitu.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Použití: python nastroje/zpracuj_fotky.py <id-druhu>")
        sys.exit(1)
    sys.exit(zpracuj(sys.argv[1]))
