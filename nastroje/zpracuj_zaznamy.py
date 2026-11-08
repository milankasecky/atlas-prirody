"""
Převod textových karet hub (nove-zaznamy/*.txt) do aplikace.

Použití:
    python nastroje/zpracuj_zaznamy.py            – zpracuje všechny karty
    python nastroje/zpracuj_zaznamy.py --kontrola – jen zkontroluje karty, nic neuloží
    python nastroje/zpracuj_zaznamy.py --vzor     – jen znovu vytvoří vzorovou kartu

Co skript udělá:
  1. Přečte všechny karty nove-zaznamy/<id>.txt (soubory začínající "_"
     přeskočí – to je vzor) a zkontroluje je proti číselníkům
     v data/hodnoty.json.
  2. Když je v JAKÉKOLIV kartě chyba, NIC neuloží a vypíše, co opravit.
  3. Zpracuje fotky z nove-fotky/<id>/ (zmenšení, odstranění EXIF/GPS,
     ověření) – stejně jako nastroje/zpracuj_fotky.py.
  4. Teprve když je vše v pořádku, uloží data/houby/<id>.json, doplní
     id do data/houby/index.json, originály fotek přesune do
     archiv-fotky/<id>/ a karty do archiv-zaznamy/.

Pole "Soukromé:" se do aplikace NIKDY nepřevádí (zůstane jen v kartě
v archiv-zaznamy/, která se nenahrává na GitHub).
"""

import difflib
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from PIL import Image

# Pomocné funkce pro fotky převezmeme z už odzkoušeného nástroje.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import zpracuj_fotky as fotky  # noqa: E402

KOREN = fotky.KOREN
SLOZKA_KARET = KOREN / "nove-zaznamy"
SLOZKA_ARCHIVU_KARET = KOREN / "archiv-zaznamy"
SLOZKA_NOVYCH_FOTEK = KOREN / "nove-fotky"
SLOZKA_ARCHIVU_FOTEK = KOREN / "archiv-fotky"
SLOZKA_DAT = KOREN / "data" / "houby"
SLOZKA_FOTEK = KOREN / "fotky" / "houby"
CESTA_HODNOTY = KOREN / "data" / "hodnoty.json"
CESTA_INDEX = SLOZKA_DAT / "index.json"
VZOR_V_NASTROJICH = KOREN / "nastroje" / "vzor-karty-houby.txt"
VZOR_V_KARTACH = SLOZKA_KARET / "_vzor-karty-houby.txt"

SOUKROME = "Soukromé"

# Pole karty: název na kartě -> (klíč v JSON, druh hodnoty)
#   text      – volný text
#   seznam    – volné hodnoty oddělené čárkou
#   ciselnik1 – jedna hodnota z číselníku
#   ciselnikN – víc hodnot z číselníku oddělených čárkou
POLE = {
    "Název česky": ("nazevCesky", "text"),
    "Název latinsky": ("nazevLatinsky", "text"),
    "Jedlost": ("jedlost", "ciselnik1:jedlost"),
    "Léčivá": ("lecive", "ano-ne"),
    "Měsíce výskytu": ("mesiceVyskytu", "ciselnikN:mesice"),
    "Stanoviště": ("stanoviste", "ciselnikN:stanoviste"),
    "Stromy": ("stromy", "ciselnikN:stromy"),
    "Určovací znaky": ("popis", "text"),
    "Záměna s": ("zamenyS", "text"),
    "Záměna odkaz": ("zamenyId", "odkazy"),
    "Štítky": ("stitky", "seznam"),
    "Nález datum": ("nalez_datum", "datum"),
    "Nález místo": ("nalez_misto", "text"),
    "Nález podmínky": ("nalez_podminky", "text"),
    SOUKROME: (None, "soukrome"),
}
POVINNA = ["Název česky", "Jedlost"]


# ------------------------------------------------------------------
# Pomocné funkce
# ------------------------------------------------------------------

def normalizuj(text):
    """Malá písmena, bez diakritiky, pomlčky/mezery sjednocené – pro porovnání."""
    bez_diakritiky = unicodedata.normalize("NFKD", text)
    bez_diakritiky = "".join(z for z in bez_diakritiky if not unicodedata.combining(z))
    return re.sub(r"[\s_\-–]+", " ", bez_diakritiky.lower()).strip()


def navrhni_id(nazev):
    """Z českého názvu udělá id, např. 'Hřib smrkový' -> 'hrib-smrkovy'."""
    return re.sub(r"[^a-z0-9]+", "-", normalizuj(nazev)).strip("-")


def nacti_json(cesta):
    return json.loads(cesta.read_text(encoding="utf-8"))


def zapis_json(cesta, data):
    cesta.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def precti_text(cesta):
    """Přečte kartu – zvládne UTF-8 (i s BOM z Poznámkového bloku) i starší kódování Windows."""
    surova = cesta.read_bytes()
    try:
        return surova.decode("utf-8-sig")
    except UnicodeDecodeError:
        return surova.decode("cp1250")


def rozdel_carkami(hodnota):
    return [cast.strip() for cast in re.split(r"[,;]", hodnota) if cast.strip()]


# ------------------------------------------------------------------
# Vzorová karta
# ------------------------------------------------------------------

def vypis_hodnot(seznam):
    return ", ".join(f"{h['nazev']} ({h['id']})" for h in seznam)


def vytvor_vzor(hodnoty):
    radky = [
        "# =================================================================",
        "#  KARTA HOUBY – vzor pro nový záznam do Atlasu přírody",
        "# =================================================================",
        "# Jak na to:",
        "#  1. Zkopíruj tento soubor do složky nove-zaznamy/ a přejmenuj ho",
        "#     na id houby: malá písmena bez diakritiky, slova oddělená",
        "#     pomlčkou, např. hrib-smrkovy.txt",
        "#  2. Fotky (pokud máš) dej do nove-fotky/<stejný název>/,",
        "#     např. nove-fotky/hrib-smrkovy/  (formát .jpg, .jpeg nebo .png)",
        "#  3. Vyplň hodnoty za dvojtečku. Řádky začínající # jsou jen",
        "#     nápověda, nikam se nepřevádí (klidně je smaž).",
        "#  4. Víc hodnot odděl čárkou. Delší text může pokračovat na",
        "#     dalších řádcích. Nevyplněné pole nech prázdné.",
        "#  5. Řekni Claudovi: „zpracuj nové záznamy“.",
        "#",
        "# Hodnoty z nabídky můžeš psát názvem (Jehličnatý les) i zkratkou",
        "# v závorce (les-jehlicnaty). Velká/malá písmena ani diakritika",
        "# nevadí. Hodnota mimo nabídku = karta se neuloží a dozvíš se,",
        "# co opravit.",
        "# -----------------------------------------------------------------",
        "",
        "# POVINNÉ. Např. Hřib smrkový",
        "Název česky: ",
        "",
        "# Např. Boletus edulis",
        "Název latinsky: ",
        "",
        "# POVINNÉ, právě jedna hodnota:",
        f"# {vypis_hodnot(hodnoty['jedlost'])}",
        "Jedlost: ",
        "",
        "# ano / ne (když nevyplníš, platí ne)",
        "Léčivá: ne",
        "",
        "# Víc hodnot čárkou, nebo rozsah pomlčkou (např. červen-říjen):",
        f"# {vypis_hodnot(hodnoty['mesice'])}",
        "Měsíce výskytu: ",
        "",
        "# Víc hodnot čárkou:",
        f"# {vypis_hodnot(hodnoty['stanoviste'])}",
        "Stanoviště: ",
        "",
        "# Mykorhizní stromy, víc hodnot čárkou:",
        f"# {vypis_hodnot(hodnoty['stromy'])}",
        "Stromy: ",
        "",
        "# Znaky, na které se houbař musí zaměřit, aby druh bezpečně",
        "# určil (např. barva rourek, síťka na třeni, vůně, změna barvy",
        "# po rozkrojení). Vzhled je vidět z fotek. Může mít víc řádků.",
        "Určovací znaky: ",
        "",
        "# Čím se liší od podobných druhů (volný text)",
        "Záměna s: ",
        "",
        "# Odkazy na podobné druhy, které už v aplikaci jsou – id nebo",
        "# český název, víc čárkou. Např. hrib-smrkovy",
        "Záměna odkaz: ",
        "",
        "# Volné štítky, víc čárkou",
        "Štítky: ",
        "",
        "# --- Vlastní nález (VEŘEJNÝ – uvidí ho každý v aplikaci) ---",
        "# Datum ve tvaru 2026-09-12 nebo 12. 9. 2026",
        "Nález datum: ",
        "# Piš obecně (např. smrkový les, okraj mlází). Přesné místo",
        "# patří do pole Soukromé níže!",
        "Nález místo: ",
        "# Počasí, podmínky",
        "Nález podmínky: ",
        "",
        "# --- SOUKROMÉ – do aplikace se NIKDY nepřevádí ---",
        "# Tvoje lokality, GPS, osobní poznámky. Může mít víc řádků.",
        "# Zůstane jen v kartě v archiv-zaznamy/ (nenahrává se na GitHub).",
        f"{SOUKROME}: ",
        "",
    ]
    text = "\n".join(radky)
    VZOR_V_NASTROJICH.write_text(text, encoding="utf-8")
    SLOZKA_KARET.mkdir(exist_ok=True)
    VZOR_V_KARTACH.write_text(text, encoding="utf-8")


# ------------------------------------------------------------------
# Čtení a kontrola karty
# ------------------------------------------------------------------

def rozparsuj_kartu(text, chyby):
    """Rozdělí kartu na pole. Vrátí {název pole: (hodnota, číslo řádku)}."""
    nazvy_podle_klice = {normalizuj(n): n for n in POLE}
    # Starší název pole – karty s "Popis:" fungují dál.
    nazvy_podle_klice[normalizuj("Popis")] = "Určovací znaky"
    pole = {}
    aktualni = None

    for cislo, radek in enumerate(text.splitlines(), start=1):
        if radek.lstrip().startswith("#"):
            continue
        shoda = re.match(r"^\s*([^:#]{1,30}?)\s*:(.*)$", radek)
        if shoda:
            nazev = nazvy_podle_klice.get(normalizuj(shoda.group(1)))
            if nazev:
                if nazev in pole:
                    chyby.append(f"řádek {cislo}: pole „{nazev}“ je v kartě dvakrát")
                pole[nazev] = (shoda.group(2).strip(), cislo)
                aktualni = nazev
                continue
            # Vypadá to jako pole s překlepem? (Mimo soukromou část.)
            if aktualni != SOUKROME:
                podobne = difflib.get_close_matches(
                    normalizuj(shoda.group(1)), nazvy_podle_klice, n=1, cutoff=0.75)
                if podobne:
                    chyby.append(
                        f"řádek {cislo}: neznámé pole „{shoda.group(1).strip()}“ – "
                        f"nemá být „{nazvy_podle_klice[podobne[0]]}“?")
                    continue
        # Pokračování textu předchozího pole na dalším řádku.
        if aktualni and radek.strip():
            hodnota, zacatek = pole[aktualni]
            pole[aktualni] = ((hodnota + "\n" + radek.strip()).strip(), zacatek)
        elif radek.strip():
            chyby.append(f"řádek {cislo}: text mimo jakékoliv pole – chybí název pole s dvojtečkou")
    return pole


def najdi_v_ciselniku(hodnota, seznam):
    hledana = normalizuj(hodnota)
    for polozka in seznam:
        if hledana in (normalizuj(polozka["id"]), normalizuj(polozka["nazev"])):
            return polozka["id"]
    return None


def preved_hodnoty_ciselniku(nazev, hodnota, cislo, ciselnik, seznam, chyby):
    vysledek = []
    for cast in rozdel_carkami(hodnota):
        # Rozsah měsíců, např. "červen-říjen".
        rozsah = re.match(r"^(\S+)\s*[-–]\s*(\S+)$", cast) if ciselnik == "mesice" else None
        if rozsah:
            od = najdi_v_ciselniku(rozsah.group(1), seznam)
            do = najdi_v_ciselniku(rozsah.group(2), seznam)
            if od and do:
                ids = [p["id"] for p in seznam]
                i, j = ids.index(od), ids.index(do)
                usek = ids[i:j + 1] if i <= j else ids[i:] + ids[:j + 1]
                vysledek += [m for m in usek if m not in vysledek]
                continue
        nalezeno = najdi_v_ciselniku(cast, seznam)
        if nalezeno:
            if nalezeno not in vysledek:
                vysledek.append(nalezeno)
        else:
            chyby.append(
                f"řádek {cislo}, pole „{nazev}“: hodnota „{cast}“ není v seznamu povolených.\n"
                f"      Povolené: {vypis_hodnot(seznam)}")
    return vysledek


def preved_datum(hodnota):
    for format_data in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(hodnota.replace(" ", ""), format_data).date().isoformat()
        except ValueError:
            pass
    return None


def zkontroluj_kartu(cesta, hodnoty, existujici, ids_karet):
    """Vrátí (zaznam, seznam_fotek, chyby). Záznam je None, pokud jsou chyby."""
    chyby = []
    id_druhu = cesta.stem
    pole = rozparsuj_kartu(precti_text(cesta), chyby)

    # --- id = název souboru ---
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", id_druhu):
        navrh = navrhni_id(pole.get("Název česky", ("",))[0]) or navrhni_id(id_druhu)
        chyby.append(
            f"název souboru „{cesta.name}“ není platné id (jen malá písmena bez diakritiky, "
            f"číslice a pomlčky). Přejmenuj kartu např. na „{navrh}.txt“ "
            f"(a stejně i složku s fotkami).")

    stary = existujici.get(id_druhu)
    if stary is not None and not stary.get("testovaciZaznam"):
        chyby.append(
            f"houba „{id_druhu}“ už v aplikaci je jako skutečný záznam – karta by ji přepsala. "
            f"Zvol jiný název karty, nebo záznam uprav ručně.")

    for nazev in POVINNA:
        if not pole.get(nazev, ("",))[0]:
            chyby.append(f"chybí povinné pole „{nazev}“")

    zaznam = {
        "id": id_druhu,
        "skupina": "houba",
        "nazevCesky": "",
        "nazevLatinsky": "",
        "mesiceVyskytu": [],
        "stanoviste": [],
        "popis": "",
        "zamenyS": "",
        "zamenyId": [],
        "fotky": list(stary.get("fotky", [])) if stary else [],
        "zaznamyNalezu": [],
        "stitky": [],
        "jedlost": "",
        "lecive": False,
        "stromy": [],
        "testovaciZaznam": False,
    }
    nalez = {}

    for nazev, (hodnota, cislo) in pole.items():
        klic, druh = POLE[nazev]
        if druh == "soukrome" or not hodnota:
            continue  # Soukromé pole se záměrně nikam nepřevádí.
        if druh == "text":
            if klic.startswith("nalez_"):
                nalez[klic[6:]] = hodnota
            else:
                zaznam[klic] = hodnota
        elif druh == "seznam":
            zaznam[klic] = rozdel_carkami(hodnota)
        elif druh == "ano-ne":
            if normalizuj(hodnota) in ("ano", "a", "yes"):
                zaznam[klic] = True
            elif normalizuj(hodnota) in ("ne", "n", "no"):
                zaznam[klic] = False
            else:
                chyby.append(f"řádek {cislo}, pole „{nazev}“: napiš „ano“ nebo „ne“, ne „{hodnota}“")
        elif druh == "datum":
            iso = preved_datum(hodnota)
            if iso:
                nalez["datum"] = iso
            else:
                chyby.append(
                    f"řádek {cislo}, pole „{nazev}“: datum „{hodnota}“ nerozumím – "
                    f"piš 2026-09-12 nebo 12. 9. 2026")
        elif druh.startswith("ciselnik"):
            pocet, ciselnik = druh[len("ciselnik"):].split(":")
            ids = preved_hodnoty_ciselniku(nazev, hodnota, cislo, ciselnik, hodnoty[ciselnik], chyby)
            if pocet == "1":
                if len(rozdel_carkami(hodnota)) > 1:
                    chyby.append(f"řádek {cislo}, pole „{nazev}“: smí obsahovat jen JEDNU hodnotu")
                zaznam[klic] = ids[0] if ids else ""
            else:
                zaznam[klic] = ids
        elif druh == "odkazy":
            for cast in rozdel_carkami(hodnota):
                cil = najdi_odkaz(cast, existujici, ids_karet)
                if cil:
                    if cil == id_druhu:
                        chyby.append(f"řádek {cislo}, pole „{nazev}“: houba nemůže odkazovat sama na sebe")
                    elif cil not in zaznam["zamenyId"]:
                        zaznam["zamenyId"].append(cil)
                else:
                    chyby.append(
                        f"řádek {cislo}, pole „{nazev}“: „{cast}“ v aplikaci není.\n"
                        f"      Existující: {', '.join(sorted(set(existujici) | ids_karet))}")

    if nalez:
        zaznam["zaznamyNalezu"].append({
            "datum": nalez.get("datum", ""),
            "misto": nalez.get("misto", ""),
            "podminky": nalez.get("podminky", ""),
        })

    fotky_druhu = zkontroluj_fotky(id_druhu, chyby)
    return (None if chyby else zaznam), fotky_druhu, chyby


def najdi_odkaz(text, existujici, ids_karet):
    hledany = normalizuj(text)
    for id_ in set(existujici) | ids_karet:
        if hledany == normalizuj(id_):
            return id_
    for id_, data in existujici.items():
        if hledany == normalizuj(data.get("nazevCesky", "")):
            return id_
    return None


def zkontroluj_fotky(id_druhu, chyby):
    """Ověří, že všechny soubory ve složce s fotkami jdou otevřít jako obrázek."""
    slozka = SLOZKA_NOVYCH_FOTEK / id_druhu
    if not slozka.is_dir():
        return []
    vysledek = []
    for soubor in sorted(slozka.iterdir()):
        if not soubor.is_file() or soubor.name.lower() in ("thumbs.db", "desktop.ini", ".ds_store"):
            continue
        if soubor.suffix.lower() not in fotky.PRIPONY_OBRAZKU:
            chyby.append(
                f"fotka „{soubor.name}“ ve složce nove-fotky/{id_druhu}/ má nepodporovaný formát – "
                f"převeď ji na .jpg (nebo ji ze složky vyndej)")
            continue
        try:
            with Image.open(soubor) as obrazek:
                obrazek.verify()
            vysledek.append(soubor)
        except Exception:
            chyby.append(f"fotku „{soubor.name}“ ve složce nove-fotky/{id_druhu}/ nejde otevřít – je poškozená?")
    return vysledek


# ------------------------------------------------------------------
# Zpracování fotek (stejný postup jako nastroje/zpracuj_fotky.py)
# ------------------------------------------------------------------

def vytvor_fotky(id_druhu, originaly, vytvorene_soubory):
    """Vytvoří malé/velké verze bez metadat. Vrátí seznam základů názvů."""
    cislo = fotky.najdi_dalsi_volne_cislo(SLOZKA_FOTEK, id_druhu)
    zaklady = []
    for original in originaly:
        zaklad = f"{id_druhu}-{cislo}"
        cesta_mala = SLOZKA_FOTEK / f"{zaklad}-mala.jpg"
        cesta_velka = SLOZKA_FOTEK / f"{zaklad}-velka.jpg"
        with Image.open(original) as obrazek:
            obrazek = fotky.ImageOps.exif_transpose(obrazek)
            fotky.uloz_bez_metadat(fotky.zmenseny_obrazek(obrazek, fotky.MALA_MAX_PX), cesta_mala, fotky.KVALITA_MALA)
            vytvorene_soubory.append(cesta_mala)
            fotky.uloz_bez_metadat(fotky.zmenseny_obrazek(obrazek, fotky.VELKA_MAX_PX), cesta_velka, fotky.KVALITA_VELKA)
            vytvorene_soubory.append(cesta_velka)
        print(f"    {original.name} -> {cesta_mala.name}, {cesta_velka.name}")
        zaklady.append(zaklad)
        cislo += 1
    return zaklady


def presun_do_archivu(soubor, slozka_archivu):
    slozka_archivu.mkdir(parents=True, exist_ok=True)
    cil = slozka_archivu / soubor.name
    if cil.exists():
        cil = slozka_archivu / f"{soubor.stem}-{datetime.now():%Y%m%d-%H%M%S}{soubor.suffix}"
    shutil.move(str(soubor), str(cil))
    return cil


# ------------------------------------------------------------------
# Hlavní běh
# ------------------------------------------------------------------

def main(jen_kontrola):
    hodnoty = nacti_json(CESTA_HODNOTY)
    vytvor_vzor(hodnoty)  # vzor je vždy v souladu s aktuálním hodnoty.json

    karty = sorted(p for p in SLOZKA_KARET.glob("*.txt") if not p.name.startswith("_"))
    if not karty:
        print("Ve složce nove-zaznamy/ nejsou žádné karty k zpracování.")
        print(f"Vzor najdeš v {VZOR_V_KARTACH.relative_to(KOREN)}")
        return 0

    index = nacti_json(CESTA_INDEX)
    existujici = {id_: nacti_json(SLOZKA_DAT / f"{id_}.json")
                  for id_ in index["seznam"] if (SLOZKA_DAT / f"{id_}.json").exists()}
    ids_karet = {k.stem for k in karty if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", k.stem)}

    # ---- 1. Kontrola všech karet – při jakékoliv chybě se nic neukládá ----
    print(f"Kontroluji karty ({len(karty)})...")
    pripravene = []
    vsechny_chyby = {}
    for karta in karty:
        zaznam, originaly, chyby = zkontroluj_kartu(karta, hodnoty, existujici, ids_karet)
        if chyby:
            vsechny_chyby[karta.name] = chyby
        else:
            pripravene.append((karta, zaznam, originaly))
            print(f"  [OK] {karta.name}  (fotek: {len(originaly)})")

    if vsechny_chyby:
        print()
        print("NIC NEBYLO ULOŽENO – v kartách jsou chyby. Oprav prosím:")
        for nazev, chyby in vsechny_chyby.items():
            print(f"\n  {nazev}:")
            for chyba in chyby:
                print(f"    - {chyba}")
        return 1

    if jen_kontrola:
        print("\nVšechny karty jsou v pořádku (jen kontrola, nic se neuložilo).")
        return 0

    # ---- 2. Fotky: zmenšit, odstranit metadata, ověřit ----
    SLOZKA_FOTEK.mkdir(parents=True, exist_ok=True)
    vytvorene_soubory = []
    print("\nZpracovávám fotky...")
    for karta, zaznam, originaly in pripravene:
        if originaly:
            print(f"  {zaznam['id']}:")
            zaznam["fotky"] += vytvor_fotky(zaznam["id"], originaly, vytvorene_soubory)

    vadne = [c.name for c in vytvorene_soubory if any(fotky.ma_soubor_exif_nebo_gps(c))]
    if vadne:
        for cesta in vytvorene_soubory:
            cesta.unlink(missing_ok=True)
        print("\nPOZOR: některé fotky stále obsahují metadata (EXIF/GPS):", ", ".join(vadne))
        print("NIC NEBYLO ULOŽENO, vytvořené fotky jsem smazal, originály zůstaly na místě.")
        return 2
    if vytvorene_soubory:
        print(f"  Ověřeno: {len(vytvorene_soubory)} souborů bez EXIF a bez GPS.")

    # ---- 3. Uložení záznamů do aplikace ----
    print("\nUkládám záznamy do aplikace...")
    for karta, zaznam, originaly in pripravene:
        zapis_json(SLOZKA_DAT / f"{zaznam['id']}.json", zaznam)
        if zaznam["id"] not in index["seznam"]:
            index["seznam"].append(zaznam["id"])
        nahrazeno = " (nahradil testovací záznam)" if zaznam["id"] in existujici else ""
        print(f"  data/houby/{zaznam['id']}.json{nahrazeno}")
    zapis_json(CESTA_INDEX, index)

    # ---- 4. Archivace originálů fotek a karet ----
    for karta, zaznam, originaly in pripravene:
        for original in originaly:
            presun_do_archivu(original, SLOZKA_ARCHIVU_FOTEK / zaznam["id"])
        slozka = SLOZKA_NOVYCH_FOTEK / zaznam["id"]
        if slozka.is_dir() and not any(slozka.iterdir()):
            slozka.rmdir()
        presun_do_archivu(karta, SLOZKA_ARCHIVU_KARET)

    print(f"\nHotovo. Zpracováno karet: {len(pripravene)}. Karty jsou v archiv-zaznamy/,")
    print("originály fotek v archiv-fotky/. Teď je bezpečné uložit změny do gitu.")
    return 0


if __name__ == "__main__":
    argumenty = sys.argv[1:]
    if argumenty == ["--vzor"]:
        vytvor_vzor(nacti_json(CESTA_HODNOTY))
        print(f"Vzor vytvořen: {VZOR_V_KARTACH.relative_to(KOREN)}")
        sys.exit(0)
    if argumenty not in ([], ["--kontrola"]):
        print(__doc__)
        sys.exit(1)
    sys.exit(main(jen_kontrola=argumenty == ["--kontrola"]))
