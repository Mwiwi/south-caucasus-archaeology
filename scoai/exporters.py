"""
Open Science exporters for GeoJSON, Linked Places / Pelagios JSON-LD,
XRONOS-compatible radiocarbon CSV tables, and spatial proximity networks.
"""

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
from scoai.radiocarbon import LAB_INSTITUTION_METADATA, calibrate_2sigma_bce
from scoai.schema import ArchaeologicalSiteRecord


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance in kilometers between two WGS84 points."""
    r_earth = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return round(2.0 * r_earth * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)), 2)


def find_nearest_neighbors(
    target: ArchaeologicalSiteRecord,
    catalog: List[ArchaeologicalSiteRecord],
    top_k: int = 3,
) -> List[Tuple[str, str, float]]:
    """Returns the top-k geographically closest sites as (site_id, name_en, distance_km)."""
    distances = []
    for candidate in catalog:
        if candidate.site_id == target.site_id:
            continue
        dist = haversine_km(target.latitude, target.longitude, candidate.latitude, candidate.longitude)
        distances.append((candidate.site_id, candidate.name_en, dist))
    distances.sort(key=lambda item: item[2])
    return distances[:top_k]


def export_geojson_collection(records: List[ArchaeologicalSiteRecord], output_path: Path) -> None:
    """Exports site records as an RFC 7946 GeoJSON FeatureCollection."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for rec in records:
        rec.validate()
    collection = {
        "type": "FeatureCollection",
        "metadata": {
            "project": "South Caucasus Open Archaeology Initiative (SCOAI)",
            "author": "Willi Ker",
            "license": "CC-BY-4.0",
            "site_count": len(records),
            "radiocarbon_sample_count": sum(len(r.radiocarbon_samples) for r in records),
            "inscription_count": sum(len(r.inscriptions) for r in records),
        },
        "features": [record.to_geojson_feature() for record in records],
    }
    output_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_pelagios_jsonld(records: List[ArchaeologicalSiteRecord], output_path: Path) -> None:
    """
    Exports archaeological sites in Linked Places / Pelagios JSON-LD gazetteer format,
    interoperable with Pleiades and World Historical Gazetteer (WHG).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features = []
    for rec in records:
        names = [{"toponym": rec.name_en, "lang": "en"}]
        if rec.name_ka:
            names.append({"toponym": rec.name_ka, "lang": "ka"})

        features.append(
            {
                "@id": f"https://github.com/Mwiwi/south-caucasus-archaeology/sites/{rec.site_id}",
                "type": "Feature",
                "properties": {
                    "title": rec.name_en,
                    "ccodes": ["GE"],
                    "period": rec.cultural_period,
                    "chronology": rec.chronology_bce,
                },
                "names": names,
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(rec.longitude, 5), round(rec.latitude, 5)],
                },
                "descriptions": [
                    {
                        "value": rec.metadata.get("significance", ""),
                        "lang": "en",
                    }
                ],
                "citations": [{"label": src} for src in rec.source_archives],
            }
        )

    doc: Dict[str, object] = {
        "@context": "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld",
        "type": "FeatureCollection",
        "features": features,
    }
    output_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_xronos_csv(records: List[ArchaeologicalSiteRecord], output_path: Path) -> int:
    """
    Exports all normalized radiocarbon (14C) samples across the catalog into a CSV file
    aligned with the global XRONOS (xronos.ch) open chronometric repository schema.
    Returns total exported 14C rows.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "labnr",
        "bp",
        "std",
        "cal_2sigma_range",
        "site_id",
        "site",
        "site_ka",
        "country",
        "region",
        "lat",
        "lng",
        "period",
        "material",
        "context_stratum",
        "lab_institution",
        "source_archive",
    ]
    row_count = 0
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for site in records:
            for sample in site.radiocarbon_samples:
                prefix = sample.lab_code.split("-")[0]
                cal_range = sample.calibrated_bce_range or calibrate_2sigma_bce(
                    sample.bp_uncalibrated, sample.std_dev
                )
                writer.writerow(
                    {
                        "labnr": sample.lab_code,
                        "bp": sample.bp_uncalibrated,
                        "std": sample.std_dev,
                        "cal_2sigma_range": cal_range,
                        "site_id": site.site_id,
                        "site": site.name_en,
                        "site_ka": site.name_ka or "",
                        "country": "GE",
                        "region": site.region,
                        "lat": site.latitude,
                        "lng": site.longitude,
                        "period": site.cultural_period,
                        "material": sample.material,
                        "context_stratum": sample.context_stratum or "",
                        "lab_institution": LAB_INSTITUTION_METADATA.get(prefix, "International AMS Laboratory"),
                        "source_archive": "; ".join(site.source_archives),
                    }
                )
                row_count += 1
    return row_count
