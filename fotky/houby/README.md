# Fotky hub

Sem se ukládají zpracované fotky ke záznamům z `data/houby/`. Nevkládej
sem fotky ručně – vznikají automaticky pomocí `nastroje/zpracuj_fotky.py`
(viz CLAUDE.md, sekce "Zpracování fotek").

Ke každému základu názvu z pole `fotky` v JSON záznamu (např.
`hrib-smrkovy-1`) existují dva soubory:

- `hrib-smrkovy-1-mala.jpg` – zmenšená verze pro náhled v seznamu
- `hrib-smrkovy-1-velka.jpg` – větší verze pro detail

Obě verze jsou bez EXIF/GPS metadat.
