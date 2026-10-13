# South Caucasus Open Archaeology Initiative (SCOAI)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23352857.svg)](https://doi.org/10.5281/zenodo.23352857)
[![SCOAI Validation & Tests](https://github.com/Mwiwi/south-caucasus-archaeology/actions/workflows/ci.yml/badge.svg)](https://github.com/Mwiwi/south-caucasus-archaeology/actions/workflows/ci.yml)
[![Benchmark: CaucasusArch-Bench](https://img.shields.io/badge/CaucasusArch--Bench-5%2F5_Passed-brightgreen.svg)](benchmarks/caucasus_arch_bench.py)
[![ORCID: 0009-0007-1720-0198](https://img.shields.io/badge/ORCID-0009--0007--1720--0198-A6CE39.svg)](https://orcid.org/0009-0007-1720-0198)
[![License: MIT](https://img.shields.io/badge/Code_License-MIT-blue.svg)](LICENSE)
[![Dataset License: CC BY 4.0](https://img.shields.io/badge/Data_License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Lead Researcher:** Willi Ker ([ORCID: 0009-0007-1720-0198](https://orcid.org/0009-0007-1720-0198))  
**Affiliation:** Independent Researcher — South Caucasus Open Archaeology Initiative (Tbilisi, Georgia)  
**Research Area:** Computational Archaeology, Cultural Heritage Preservation, Spatial-Temporal Data Synthesis  
**Archival DOI (CERN Zenodo):** [10.5281/zenodo.23352857](https://doi.org/10.5281/zenodo.23352857)

---

## Overview

The **South Caucasus Open Archaeology Initiative (SCOAI)** is an independent, non-commercial computational research project dedicated to digitizing, standardizing, and synthesizing archaeological, chronometric ($^{14}\text{C}$), paleoenvironmental, and epigraphic records across Georgia and the broader South Caucasus region.

Critical archaeological and chronometric data from the South Caucasus—spanning Early Pleistocene hominin dispersals (Dmanisi, Orozmani), Neolithic viniculture (Shulaveri-Shomu), Bronze Age metallurgy and kurgan horizons (Kura-Araxes, Bedeni, Trialeti, Colchis), and ancient epigraphy (*Asomtavruli*, *Armazic Aramaic*, Greek)—remain fragmented across unindexed Georgian and historical multilingual archival monographs. Because legacy laboratory radiocarbon records (e.g., Tbilisi `Tb-` / `თბ-` and `LE-` series), stratigraphic tables, and historical DMS coordinates lack standardized digitization, the South Caucasus remains heavily underrepresented in global open-science repositories such as **XRONOS** and **Pleiades / Pelagios**.

---

## Agentic Self-Correction Architecture (Google Antigravity + Gemini 4 Argon)

Digitizing legacy 1950s–1980s archaeological tables and epigraphic plates with single-pass OCR/LLM extraction frequently introduces leading-digit corruptions in radiocarbon ages (e.g., `6850 BP` misread as `3850 BP` on degraded scans) or glyph substitutions in *Asomtavruli* inscriptions.

SCOAI implements a **3-turn Agentic Self-Correction Loop** (`scoai/agent_workflow.py` + `scoai/stratigraphy.py`):

1. **Turn 1 — Multimodal & Cross-Lingual Extraction:** Gemini 4 Argon extracts structured site metadata, DMS coordinates, stratigraphic levels (`ფენა` / `Stratum`), and radiocarbon determinations.
2. **Turn 2 — Physical & Statistical Chronometric Critique:**
   - **Law of Superposition Verifier (`verify_stratigraphic_superposition`):** Checks that deeper strata do not exhibit statistically younger ($>2\sigma$) radiocarbon ages than overlying horizons.
   - **Ward & Wilson (1978) $\chi^2$ Phase Coherence Test (`ward_wilson_chi2_test`):** Computes pooled radiocarbon means $\bar{t}$ and test statistic $T = \sum (t_i - \bar{t})^2 / \sigma_i^2 \sim \chi^2_{n-1}$ (Archaeometry 20(1): 19–31) to isolate outlier samples within coeval horizons.
3. **Turn 3 — Agentic Critique & OCR Repair:** When an inversion or $\chi^2$ rejection is detected, the agent constructs a diagnostic critique prompt and evaluates OCR digit confusion hypotheses to restore stratigraphic superposition and statistical coherence.

---

## Key Research Domains

1. **Early Pleistocene & Paleolithic Dispersals:** Aggregating stratigraphic, radiometric, and paleoenvironmental metadata across Lower, Middle, and Upper Paleolithic sites in Kvemo Kartli and Imereti (*Dmanisi*, *Orozmani*, *Dzudzuana Cave*, *Ortvale Klde*).
2. **Neolithic Viniculture & Agrarian Tells:** Mapping ceramic, archaeobotanical, and $^{14}\text{C}$ records across Shulaveri-Shomu culture settlements (*Gadachrili Gora*, *Shulaveris Gora*, *Khramis Didi-Gora*, *Arukhlo I*, *Imiris Gora*).
3. **Metallurgy & Bronze Age Kurgan Networks:** Structuring chronologies and spatial distributions across Kura-Araxes, Bedeni, Trialeti, and Colchian cultural complexes (*Sakdrisi-Kachagiani*, *Kvatskhelebi*, *Berikldeebi*, *Bedeni*, *Ananauri*, *Trialeti*, *Vani*, *Grakliani Hill*).
4. **Epigraphy & Script Transliteration:** Cross-lingual optical character recognition (OCR), bidirectional Unicode script conversion (*Asomtavruli* `ႠႱႭႫႧႠႥႰႳႪႨ` $\leftrightarrow$ *Nuskhuri* `ⴀⴑⴍⴋⴇⴀⴅⴐⴓⴊⴈ` $\leftrightarrow$ *Mkhedruli* `ასომთავრული` $\leftrightarrow$ scholarly Kartvelological Latin), and structured cataloging of bilingual monuments (*Bolnisi Sioni*, *Mtskheta Jvari*, *Armazi Bilingual*).

---

## Repository Structure

```text
south-caucasus-archaeology/
├── scoai/
│   ├── schema.py            # Dataclasses & Caucasus WGS84 / 14C validators
│   ├── radiocarbon.py       # Legacy lab prefix normalizer (თბ->Tb, LE, GIN, RTD) & IntCal20 calibrator
│   ├── stratigraphy.py      # Ward & Wilson (1978) chi-squared test & Law of Superposition verifier
│   ├── agent_workflow.py    # 3-turn Gemini 4 Argon agentic extraction, critique, and OCR repair loop
│   ├── epigraphy.py         # Asomtavruli / Nuskhuri / Mkhedruli converter & scholarly Latin transliterator
│   ├── archival_parser.py   # Georgian/English archival text & DMS coordinate parser + Gemini 4 Argon schema
│   ├── catalog.py           # Reference catalog of 20 major archaeological & epigraphic sites across Georgia
│   └── exporters.py         # GeoJSON, Pelagios Linked Places JSON-LD, XRONOS CSV, and Haversine spatial graph
├── benchmarks/
│   └── caucasus_arch_bench.py # CaucasusArch-Bench evaluation suite for agentic OCR repair & epigraphy
├── data/
│   ├── sites.geojson          # RFC 7946 GeoJSON FeatureCollection (rendered interactively on GitHub)
│   ├── sites_pelagios.jsonld  # Linked Open Data gazetteer compatible with Pleiades / Pelagios / WHG
│   ├── radiocarbon_xronos.csv # Standardized 14C chronometric table compatible with XRONOS (xronos.ch)
│   ├── caucasus_arch_bench_results.json # Benchmark evaluation metrics
│   └── raw_samples/           # Sample Georgian/English archival report excerpts
├── tests/
│   └── test_scoai.py        # 13 unit tests covering 14C calibration, stratigraphy, agent loop, and epigraphy
└── pipeline.py              # CLI entrypoint for validation and dataset generation
```

---

## Quick Start

### 1. Run the Normalization & Export Pipeline

```bash
python3 pipeline.py
```

### 2. Run the `CaucasusArch-Bench` Evaluation Suite

```bash
PYTHONPATH=. python3 benchmarks/caucasus_arch_bench.py
```

### 3. Run the Automated Unit Test Suite

```bash
python3 -m unittest discover -s tests -v
```

---

## License

Distributed under the **MIT License** (Code) and **CC-BY-4.0** (Datasets) for non-commercial scientific research.
