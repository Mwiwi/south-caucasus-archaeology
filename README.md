# South Caucasus Open Archaeology Initiative (SCOAI)

**Lead Researcher:** Willi Ker  
**Affiliation:** Independent Researcher — South Caucasus Open Archaeology Initiative (Tbilisi, Georgia)  
**Research Area:** Computational Archaeology, Cultural Heritage Preservation, Spatial-Temporal Data Synthesis

---

## Overview

The **South Caucasus Open Archaeology Initiative (SCOAI)** is an independent, non-commercial computational research project dedicated to digitizing, standardizing, and synthesizing archaeological, paleoenvironmental, and epigraphic records across Georgia and the broader South Caucasus region.

A vast amount of critical archaeological data from the South Caucasus—spanning Early Pleistocene hominin dispersals, Neolithic viticulture, Bronze Age metallurgy, and classical antiquity—remains locked in unindexed, multi-lingual archival publications (Georgian, Russian, German, and English) and fragmented museum catalogs. This project develops open-source data schemas, multimodal extraction workflows, and geocoded datasets to bridge archival literature with modern spatial analysis.

## Key Research Domains

1. **Early Pleistocene Hominin Dispersals:** Aggregating stratigraphic, faunal, and paleoenvironmental metadata around Lower Paleolithic sites in Kvemo Kartli and Javakheti (e.g., Dmanisi, Orozmani).
2. **Neolithic Viticulture & Agrarian Settlements:** Mapping ceramic, archaeobotanical, and radiocarbon ($^{14}\text{C}$) records across Shulaveri-Shomu culture settlements (e.g., Gadachrili Gora, Khramis Didi-Gora, Shulaveris Gora).
3. **Metallurgy & Bronze Age Networks:** Structuring artifact typologies, radiocarbon chronologies, and spatial distributions across Kura-Araxes, Trialeti, and Colchian cultural complexes (e.g., Sakdrisi-Kachagiani, Trialeti kurgans, Vani).
4. **Epigraphy & Archival Digitization:** Cross-lingual optical character recognition (OCR) and structured entity extraction for legacy archaeological reports and ancient epigraphic monuments (Armazic/Aramaic, Greek, and early Georgian Asomtavruli inscriptions).

## Methodology & AI Integration

- **Multimodal Document Parsing:** Automated extraction of stratigraphy tables, radiocarbon dates ($^{14}\text{C}$ BP / calibrated BCE), and lithic/ceramic typologies from archival monographs and field reports.
- **Geospatial Synthesis:** Correlating legacy site coordinates with modern DEM/LiDAR topography and satellite imagery to produce standardized GeoJSON and JSON-LD spatial layers.
- **Open Science Deliverables:** Releasing open-access, geocoded archaeological datasets and reproducible Python tools for the research community.

## Repository Structure

- `pipeline.py` — Core data models, radiocarbon calibration/normalization schemas, and GeoJSON export pipeline for archaeological site records.
- `data/sites.geojson` — Standardized open-access geocoded baseline dataset of key reference sites in Georgia (rendered interactively by GitHub).

## Quick Start

```bash
python3 pipeline.py
```

Running `pipeline.py` validates the site records and regenerates `data/sites.geojson`.

## License

Distributed under the MIT License (Code) and CC-BY-4.0 (Datasets) for non-commercial scientific research.
