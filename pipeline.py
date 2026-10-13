"""
South Caucasus Open Archaeology Initiative (SCOAI)
Main CLI pipeline for validating archaeological records, normalizing legacy 14C dates,
transliterating Asomtavruli epigraphy, and generating Open Science datasets
(GeoJSON, Pelagios Linked Places JSON-LD, and XRONOS radiocarbon CSV).

Author: Willi Ker
"""

import argparse
from pathlib import Path
from scoai.catalog import build_reference_catalog
from scoai.exporters import (
    export_geojson_collection,
    export_pelagios_jsonld,
    export_xronos_csv,
    find_nearest_neighbors,
)
from scoai.schema import ArchaeologicalSiteRecord, RadiocarbonSample

__all__ = ["ArchaeologicalSiteRecord", "RadiocarbonSample", "build_reference_catalog"]


def run_pipeline(data_dir: Path, verbose: bool = True) -> None:
    catalog = build_reference_catalog()
    total_c14 = sum(len(s.radiocarbon_samples) for s in catalog)
    total_epi = sum(len(s.inscriptions) for s in catalog)

    if verbose:
        print(f"=== South Caucasus Open Archaeology Initiative (SCOAI) Pipeline ===")
        print(f"Validated {len(catalog)} archaeological sites, {total_c14} 14C samples, {total_epi} inscriptions.\n")
        for site in catalog:
            neighbors = find_nearest_neighbors(site, catalog, top_k=1)
            nearest_str = f"nearest: {neighbors[0][0]} ({neighbors[0][2]} km)" if neighbors else ""
            print(
                f"  [{site.site_id}] {site.name_en} ({site.name_ka}) — {site.cultural_period} "
                f"| 14C: {len(site.radiocarbon_samples)} | {nearest_str}"
            )

    geojson_path = data_dir / "sites.geojson"
    jsonld_path = data_dir / "sites_pelagios.jsonld"
    xronos_csv_path = data_dir / "radiocarbon_xronos.csv"

    export_geojson_collection(catalog, geojson_path)
    export_pelagios_jsonld(catalog, jsonld_path)
    exported_rows = export_xronos_csv(catalog, xronos_csv_path)

    if verbose:
        print(f"\nExported Open Science deliverables:")
        print(f"  - GeoJSON FeatureCollection : {geojson_path} ({len(catalog)} features)")
        print(f"  - Pelagios JSON-LD Gazetteer: {jsonld_path} ({len(catalog)} linked places)")
        print(f"  - XRONOS 14C Chronometric DB: {xronos_csv_path} ({exported_rows} calibrated samples)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCOAI Data Normalization & Export Pipeline")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "data",
        help="Target directory for generated datasets",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed console summary")
    args = parser.parse_args()
    run_pipeline(args.output_dir, verbose=not args.quiet)
