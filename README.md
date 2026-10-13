# South Caucasus Open Archaeology Initiative (SCOAI)

**Lead Researcher:** Willi Ker  
**Affiliation:** Independent Researcher — South Caucasus Open Archaeology Initiative (Tbilisi, Georgia)  
**Research Area:** Computational Archaeology, Cultural Heritage Preservation, Spatial-Temporal Data Synthesis

---

## Overview

The **South Caucasus Open Archaeology Initiative (SCOAI)** is an independent, non-commercial computational research project dedicated to digitizing, standardizing, and synthesizing archaeological, chronometric ($^{14}\text{C}$), paleoenvironmental, and epigraphic records across Georgia and the broader South Caucasus region.

Critical archaeological and chronometric data from the South Caucasus—spanning Early Pleistocene hominin dispersals (Dmanisi, Orozmani), Neolithic viniculture (Shulaveri-Shomu), Bronze Age metallurgy and kurgan horizons (Kura-Araxes, Bedeni, Trialeti, Colchis), and ancient epigraphy (*Asomtavruli*, *Armazic Aramaic*, Greek)—remain fragmented across unindexed Georgian and historical archival monographs. Because legacy laboratory radiocarbon records (e.g., Tbilisi `Tb-` / `თბ-` and `LE-` series), stratigraphic tables, and historical DMS coordinates lack standardized digitization, the South Caucasus remains underrepresented in global open-science repositories such as **XRONOS** and **Pleiades / Pelagios**.

This repository provides an open-source Python normalization toolkit (`scoai`) and geocoded datasets bridging Caucasian archival literature with international Linked Open Data standards.

---

## Key Research Domains

1. **Early Pleistocene & Paleolithic Dispersals:** Aggregating stratigraphic, radiometric, and paleoenvironmental metadata across Lower, Middle, and Upper Paleolithic sites in Kvemo Kartli and Imereti (*Dmanisi*, *Orozmani*, *Dzudzuana Cave*, *Ortvale Klde*).
2. **Neolithic Viniculture & Agrarian Tells:** Mapping ceramic, archaeobotanical, and $^{14}\text{C}$ records across Shulaveri-Shomu culture settlements (*Gadachrili Gora*, *Shulaveris Gora*, *Khramis Didi-Gora*, *Arukhlo I*, *Imiris Gora*).
3. **Metallurgy & Bronze Age Kurgan Networks:** Structuring chronologies and spatial distributions across Kura-Araxes, Bedeni, Trialeti, and Colchian cultural complexes (*Sakdrisi-Kachagiani*, *Kvatskhelebi*, *Berikldeebi*, *Bedeni*, *Ananauri*, *Trialeti*, *Vani*, *Grakliani Hill*).
4. **Epigraphy & Script Transliteration:** Cross-lingual optical character recognition (OCR), bidirectional Unicode script conversion (*Asomtavruli* `ႠႱႭႫႧႠႥႰႳႪႨ` $\leftrightarrow$ *Nuskhuri* `ⴀⴑⴍⴋⴇⴀⴅⴐⴓⴊⴈ` $\leftrightarrow$ *Mkhedruli* `ასომთავრული` $\leftrightarrow$ scholarly Kartvelological Latin), and structured cataloging of bilingual monuments (*Bolnisi Sioni*, *Mtskheta Jvari*, *Armazi Bilingual*).

---

## Architecture & Repository Structure

```text
south-caucasus-archaeology/
├── scoai/
│   ├── schema.py            # Dataclasses & Caucasus WGS84 / 14C validators
│   ├── radiocarbon.py       # Legacy lab prefix normalizer (თბ->Tb, LE, GIN, RTD) & IntCal20 calibrator
│   ├── epigraphy.py         # Asomtavruli / Nuskhuri / Mkhedruli converter & scholarly Latin transliterator
│   ├── archival_parser.py   # Georgian/English archival text & DMS coordinate parser + Gemini 4 Argon schema
│   ├── catalog.py           # Reference catalog of 20 major archaeological & epigraphic sites across Georgia
│   └── exporters.py         # GeoJSON, Pelagios Linked Places JSON-LD, XRONOS CSV, and Haversine spatial graph
├── data/
│   ├── sites.geojson        # RFC 7946 GeoJSON FeatureCollection (rendered interactively on GitHub)
│   ├── sites_pelagios.jsonld# Linked Open Data gazetteer compatible with Pleiades / Pelagios / WHG
│   ├── radiocarbon_xronos.csv # Standardized 14C chronometric table compatible with XRONOS (xronos.ch)
│   └── raw_samples/         # Sample Georgian/English archival report excerpts
├── tests/
│   └── test_scoai.py        # Unit test suite covering 14C calibration, epigraphy, DMS parsing, and exports
└── pipeline.py              # CLI entrypoint for validation and dataset generation
```

---

## Quick Start

### 1. Run the Normalization & Export Pipeline

```bash
python3 pipeline.py
```

This validates all 20 reference sites, normalizes and calibrates the radiocarbon series, processes the epigraphic inscriptions, and generates:
- `data/sites.geojson`
- `data/sites_pelagios.jsonld`
- `data/radiocarbon_xronos.csv`

### 2. Run the Automated Test Suite

```bash
python3 -m unittest discover -s tests -v
```

---

## Example Usage

### Normalizing Legacy Georgian $^{14}\text{C}$ Records

```python
from scoai.radiocarbon import parse_archival_radiocarbon_line

sample = parse_archival_radiocarbon_line("თბ-312: 6850 ± 70 BP (ნახშირი, ფენა III)")
print(sample.lab_code)             # "Tb-312"
print(sample.material)             # "Charcoal"
print(sample.calibrated_bce_range) # "5900 - 5580 cal BCE"
```

### Transliterating Ancient Georgian *Asomtavruli* Inscriptions

```python
from scoai.epigraphy import asomtavruli_to_mkhedruli, transliterate_georgian_to_latin

inscription = "ႵႤ ႣႠႧႳႬႠ ႤႮႨႱႩႭႮႭႱႱႠ"  # Bolnisi Sioni (493-494 CE)
print(asomtavruli_to_mkhedruli(inscription))        # "ქე დათუნა ეპისკოპოსსა"
print(transliterate_georgian_to_latin(inscription)) # "ke datuna ep'isk'op'ossa"
```

---

## License

Distributed under the **MIT License** (Code) and **CC-BY-4.0** (Datasets) for non-commercial scientific research.
