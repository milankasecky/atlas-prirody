// Atlas přírody – jednoduchá aplikace pro zobrazení a filtrování hub.
// Žádné knihovny, jen čistý JavaScript.

// Stejný název cache jako v sw.js – používá se pro ruční doplnění
// všech dat a fotek, aby byly dostupné i bez internetu.
const NAZEV_CACHE = "atlas-prirody-cache";

// Globální proměnné – data se načtou jednou při startu.
let hodnoty = null; // číselníky (měsíce, stanoviště, stromy, jedlost)
let houby = []; // všechny načtené houby

// Odkazy na prvky stránky.
const el = {
  pohledSeznam: document.getElementById("pohled-seznam"),
  pohledDetail: document.getElementById("pohled-detail"),
  detailObsah: document.getElementById("detail-obsah"),
  tlacitkoZpet: document.getElementById("tlacitko-zpet"),
  seznamHub: document.getElementById("seznam-hub"),
  pocetVysledku: document.getElementById("pocet-vysledku"),
  vstupHledani: document.getElementById("vstup-hledani"),
  filtrMesic: document.getElementById("filtr-mesic"),
  filtrStanoviste: document.getElementById("filtr-stanoviste"),
  filtrStrom: document.getElementById("filtr-strom"),
  filtrJedlost: document.getElementById("filtr-jedlost"),
  filtrLecive: document.getElementById("filtr-lecive"),
  tlacitkoZrusitFiltry: document.getElementById("tlacitko-zrusit-filtry"),
  lightbox: document.getElementById("lightbox"),
  lightboxObrazek: document.getElementById("lightbox-obrazek"),
  tlacitkoZavritLightbox: document.getElementById("tlacitko-zavrit-lightbox"),
};

// ---------- Načtení dat ----------

async function nactiData() {
  hodnoty = await fetch("data/hodnoty.json").then((r) => r.json());

  const index = await fetch("data/houby/index.json").then((r) => r.json());
  houby = await Promise.all(
    index.seznam.map((id) =>
      fetch(`data/houby/${id}.json`).then((r) => r.json())
    )
  );
}

// Najde v číselníku český název podle id (např. "brezen" -> "Březen").
function nazevZCiselniku(seznamHodnot, id) {
  const nalezeno = seznamHodnot.find((h) => h.id === id);
  return nalezeno ? nalezeno.nazev : id;
}

// ---------- Naplnění filtrů z číselníků ----------

function naplnFiltrVyberem(selectEl, seznamHodnot) {
  for (const hodnota of seznamHodnot) {
    const option = document.createElement("option");
    option.value = hodnota.id;
    option.textContent = hodnota.nazev;
    selectEl.appendChild(option);
  }
}

function naplnFiltry() {
  naplnFiltrVyberem(el.filtrMesic, hodnoty.mesice);
  naplnFiltrVyberem(el.filtrStanoviste, hodnoty.stanoviste);
  naplnFiltrVyberem(el.filtrStrom, hodnoty.stromy);
  naplnFiltrVyberem(el.filtrJedlost, hodnoty.jedlost);
}

// ---------- Filtrování a hledání ----------

// Odstraní diakritiku, aby hledání fungovalo i bez háčků a čárek.
function bezDiakritiky(text) {
  return text
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

function vyfiltrujHouby() {
  const hledanyText = bezDiakritiky(el.vstupHledani.value.trim());
  const mesic = el.filtrMesic.value;
  const stanoviste = el.filtrStanoviste.value;
  const strom = el.filtrStrom.value;
  const jedlost = el.filtrJedlost.value;
  const jenLecive = el.filtrLecive.checked;

  return houby.filter((h) => {
    if (
      hledanyText &&
      !bezDiakritiky(h.nazevCesky).includes(hledanyText) &&
      !bezDiakritiky(h.nazevLatinsky).includes(hledanyText)
    ) {
      return false;
    }
    if (mesic && !h.mesiceVyskytu.includes(mesic)) return false;
    if (stanoviste && !h.stanoviste.includes(stanoviste)) return false;
    if (strom && !(h.stromy || []).includes(strom)) return false;
    if (jedlost && h.jedlost !== jedlost) return false;
    if (jenLecive && !h.lecive) return false;
    return true;
  });
}

// ---------- Vykreslení seznamu ----------

function vykresliSeznam() {
  const vyfiltrovane = vyfiltrujHouby();

  el.seznamHub.innerHTML = "";
  el.pocetVysledku.textContent = `Nalezeno: ${vyfiltrovane.length} z ${houby.length}`;

  if (vyfiltrovane.length === 0) {
    el.seznamHub.innerHTML = `<li class="prazdny-seznam">Žádná houba neodpovídá zadaným filtrům.</li>`;
    return;
  }

  for (const houba of vyfiltrovane) {
    el.seznamHub.appendChild(vytvorKartuHouby(houba));
  }
}

function vytvorKartuHouby(houba) {
  const li = document.createElement("li");
  li.className = "karta-houby";
  li.addEventListener("click", () => zobrazDetail(houba));

  const nahled = document.createElement("div");
  nahled.className = "karta-houby__nahled";
  nahled.textContent = "🍄";
  if (houba.fotky && houba.fotky.length > 0) {
    const img = document.createElement("img");
    img.src = `fotky/houby/${houba.fotky[0]}-mala.jpg`;
    img.alt = houba.nazevCesky;
    img.className = "karta-houby__nahled";
    // Pokud fotka chybí (zatím nejsou vložené), zůstane jen emoji náhled.
    img.onerror = () => img.remove();
    nahled.textContent = "";
    nahled.appendChild(img);
  }

  const info = document.createElement("div");
  info.className = "karta-houby__info";
  info.innerHTML = `
    <p class="karta-houby__nazev">${houba.nazevCesky}</p>
    <p class="karta-houby__latinsky">${houba.nazevLatinsky}</p>
    ${vytvorStitky(houba)}
  `;

  li.appendChild(nahled);
  li.appendChild(info);
  return li;
}

function vytvorStitky(houba) {
  let html = "";
  if (houba.jedlost) {
    const nazev = nazevZCiselniku(hodnoty.jedlost, houba.jedlost);
    html += `<span class="stitek stitek--${houba.jedlost}">${nazev}</span> `;
  }
  if (houba.lecive) {
    html += `<span class="stitek stitek--lecive">Léčivá</span> `;
  }
  if (houba.testovaciZaznam) {
    html += `<span class="stitek stitek--test">TESTOVACÍ ZÁZNAM</span>`;
  }
  return html;
}

// ---------- Detail houby ----------

function zobrazDetail(houba) {
  // Hlavní záznam + prázdný kontejner pro "vložené" záznamy záměn.
  el.detailObsah.innerHTML = `
    <div id="hlavni-zaznam"></div>
    <div id="navazane-zaznamy"></div>
  `;
  document.getElementById("hlavni-zaznam").innerHTML = vykresliDetail(houba);
  el.pohledSeznam.hidden = true;
  el.pohledDetail.hidden = false;
  window.scrollTo(0, 0);
}

// Najde houbu podle id v už načtených datech.
function najdiHoubuPodleId(id) {
  return houby.find((h) => h.id === id);
}

// Otevře pod aktuálním detailem vložený záznam houby, se kterou se dá zaměnit.
function otevriNavazanyZaznam(id) {
  const houba = najdiHoubuPodleId(id);
  if (!houba) return;

  const kontejner = document.getElementById("navazane-zaznamy");
  if (kontejner.querySelector(`[data-panel-id="${id}"]`)) {
    return; // tento záznam je už otevřený
  }

  const panel = document.createElement("div");
  panel.className = "panel-navazany";
  panel.dataset.panelId = id;
  panel.innerHTML = `
    <button class="tlacitko-zavrit-panel" type="button" data-zavri-panel="${id}" title="Zavřít">×</button>
    ${vykresliDetail(houba)}
  `;
  kontejner.appendChild(panel);
}

function vykresliDetail(houba) {
  const fotky =
    houba.fotky && houba.fotky.length > 0
      ? houba.fotky
          .map(
            (f) =>
              `<img src="fotky/houby/${f}-velka.jpg" alt="${houba.nazevCesky}" onerror="this.outerHTML='<div class=\\'chybi-foto\\'>🍄</div>'">`
          )
          .join("")
      : `<div class="chybi-foto">🍄</div>`;

  const mesiceText = houba.mesiceVyskytu
    .map((id) => nazevZCiselniku(hodnoty.mesice, id))
    .map((nazev) => `<span class="chip">${nazev}</span>`)
    .join("");

  const stanovisteText = houba.stanoviste
    .map((id) => nazevZCiselniku(hodnoty.stanoviste, id))
    .map((nazev) => `<span class="chip">${nazev}</span>`)
    .join("");

  const stromyText = (houba.stromy || [])
    .map((id) => nazevZCiselniku(hodnoty.stromy, id))
    .map((nazev) => `<span class="chip">${nazev}</span>`)
    .join("");

  const stitkyText = (houba.stitky || [])
    .map((stitek) => `<span class="chip">${stitek}</span>`)
    .join("");

  // Odkazy na záznamy podobných/zaměnitelných druhů – kliknutím se otevřou pod detailem.
  const zamenyOdkazy = (houba.zamenyId || [])
    .map((id) => najdiHoubuPodleId(id))
    .filter((h) => h)
    .map(
      (h) =>
        `<button class="chip chip--odkaz" type="button" data-otevri-zaznam="${h.id}">${h.nazevCesky} →</button>`
    )
    .join("");

  const zaznamyNalezuText = (houba.zaznamyNalezu || [])
    .map(
      (z) => `
        <div class="zaznam-nalezu">
          ${z.datum ? `<p class="zaznam-nalezu__datum">${z.datum}</p>` : ""}
          ${z.misto ? `<p class="zaznam-nalezu__misto">📍 ${z.misto}</p>` : ""}
          ${z.podminky ? `<p>${z.podminky}</p>` : ""}
        </div>
      `
    )
    .join("");

  return `
    <div class="detail-stitky">${vytvorStitky(houba)}</div>
    <h1 class="detail-nazev">${houba.nazevCesky}</h1>
    <p class="detail-latinsky">${houba.nazevLatinsky}</p>

    <div class="detail-fotky">${fotky}</div>

    <div class="detail-sekce">
      <h2>Určovací znaky</h2>
      <p class="viceradkovy">${houba.popis || "–"}</p>
    </div>

    <div class="detail-sekce">
      <h2>Výskyt</h2>
      <div class="chipy">${mesiceText}</div>
      <div class="chipy" style="margin-top:6px">${stanovisteText}</div>
      ${
        stromyText
          ? `<div class="chipy" style="margin-top:6px">${stromyText}</div>`
          : ""
      }
    </div>

    <div class="detail-sekce">
      <h2>Záměny</h2>
      <p class="viceradkovy">${houba.zamenyS || "–"}</p>
      ${zamenyOdkazy ? `<div class="chipy" style="margin-top:8px">${zamenyOdkazy}</div>` : ""}
    </div>

    ${
      zaznamyNalezuText
        ? `<div class="detail-sekce"><h2>Záznam nálezu</h2>${zaznamyNalezuText}</div>`
        : ""
    }

    ${
      stitkyText
        ? `<div class="detail-sekce"><h2>Štítky</h2><div class="chipy">${stitkyText}</div></div>`
        : ""
    }
  `;
}

function zobrazSeznam() {
  el.pohledDetail.hidden = true;
  el.pohledSeznam.hidden = false;
}

// ---------- Zvětšená fotka přes celou obrazovku ----------

function otevriLightbox(src, alt) {
  el.lightboxObrazek.src = src;
  el.lightboxObrazek.alt = alt;
  el.lightbox.hidden = false;
}

function zavriLightbox() {
  el.lightbox.hidden = true;
  el.lightboxObrazek.src = "";
}

// ---------- Spuštění ----------

function pripojUdalosti() {
  el.vstupHledani.addEventListener("input", vykresliSeznam);
  el.filtrMesic.addEventListener("change", vykresliSeznam);
  el.filtrStanoviste.addEventListener("change", vykresliSeznam);
  el.filtrStrom.addEventListener("change", vykresliSeznam);
  el.filtrJedlost.addEventListener("change", vykresliSeznam);
  el.filtrLecive.addEventListener("change", vykresliSeznam);
  el.tlacitkoZpet.addEventListener("click", zobrazSeznam);

  // Kliky uvnitř detailu (odkaz na záměnu / zavření vloženého panelu)
  // řešíme delegovaně, protože obsah detailu se opakovaně přegenerovává.
  el.detailObsah.addEventListener("click", (e) => {
    const fotka = e.target.closest(".detail-fotky img");
    if (fotka) {
      otevriLightbox(fotka.src, fotka.alt);
      return;
    }
    const odkazNaZamenu = e.target.closest("[data-otevri-zaznam]");
    if (odkazNaZamenu) {
      otevriNavazanyZaznam(odkazNaZamenu.dataset.otevriZaznam);
      return;
    }
    const tlacitkoZavrit = e.target.closest("[data-zavri-panel]");
    if (tlacitkoZavrit) {
      tlacitkoZavrit.closest(".panel-navazany").remove();
    }
  });

  // Zavření zvětšené fotky – klik na křížek, nebo kamkoliv do pozadí.
  el.tlacitkoZavritLightbox.addEventListener("click", zavriLightbox);
  el.lightbox.addEventListener("click", (e) => {
    if (e.target === el.lightbox) zavriLightbox();
  });

  el.tlacitkoZrusitFiltry.addEventListener("click", () => {
    el.vstupHledani.value = "";
    el.filtrMesic.value = "";
    el.filtrStanoviste.value = "";
    el.filtrStrom.value = "";
    el.filtrJedlost.value = "";
    el.filtrLecive.checked = false;
    vykresliSeznam();
  });
}

// Zaregistruje service worker, díky kterému appka funguje i bez internetu.
function zaregistrujServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}

// Při každém spuštění (pokud je internet) doplní do cache úplně všechna
// data a fotky, aby byly k dispozici i při dalším otevření bez internetu.
// Chybějící soubory (např. ještě nevložené fotky) se tiše přeskočí.
async function ulozVseProOffline() {
  if (!("caches" in window)) return;

  const zakladniSoubory = [
    "./",
    "index.html",
    "css/style.css",
    "js/app.js",
    "manifest.json",
    "icons/icon-192.png",
    "icons/icon-512.png",
    "data/hodnoty.json",
    "data/houby/index.json",
  ];
  const zaznamyHub = houby.map((h) => `data/houby/${h.id}.json`);
  const fotkyHub = houby.flatMap((h) =>
    (h.fotky || []).flatMap((f) => [
      `fotky/houby/${f}-mala.jpg`,
      `fotky/houby/${f}-velka.jpg`,
    ])
  );

  const cache = await caches.open(NAZEV_CACHE);

  await Promise.allSettled(
    [...zakladniSoubory, ...zaznamyHub, ...fotkyHub].map(async (adresa) => {
      try {
        const odpoved = await fetch(adresa);
        if (odpoved.ok) await cache.put(adresa, odpoved);
      } catch {
        // Soubor není dostupný – přeskočit bez chyby.
      }
    })
  );
}

async function start() {
  zaregistrujServiceWorker();
  await nactiData();
  naplnFiltry();
  pripojUdalosti();
  vykresliSeznam();
  ulozVseProOffline();
}

start();
