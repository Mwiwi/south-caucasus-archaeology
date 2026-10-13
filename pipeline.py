"""
South Caucasus Open Archaeology Initiative (SCOAI)
Core schema and normalization pipeline for multi-lingual archival archaeological records.
Author: Willi Ker
"""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RadiocarbonSample:
    lab_code: str
    bp_uncalibrated: int
    std_dev: int
    material: str
    calibrated_bce_range: Optional[str] = None


@dataclass
class ArchaeologicalSiteRecord:
    site_id: str
    name_en: str
    name_ka: Optional[str]
    region: str
    latitude: float
    longitude: float
    cultural_period: str  # e.g., Lower Paleolithic, Shulaveri-Shomu, Kura-Araxes, Trialeti, Colchian
    chronology_bce: str
    radiocarbon_samples: List[RadiocarbonSample] = field(default_factory=list)
    source_archives: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_geojson_feature(self) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "site_id": self.site_id,
                "name_en": self.name_en,
                "name_ka": self.name_ka,
                "region": self.region,
                "cultural_period": self.cultural_period,
                "chronology_bce": self.chronology_bce,
                "radiocarbon_samples": [asdict(s) for s in self.radiocarbon_samples],
                "sources": self.source_archives,
                "metadata": self.metadata,
            },
        }


def build_reference_catalog() -> List[ArchaeologicalSiteRecord]:
    """Returns baseline reference records for key archaeological sites in Georgia."""
    return [
        ArchaeologicalSiteRecord(
            site_id="GEO-DMN-001",
            name_en="Dmanisi Hominin Site",
            name_ka="დმანისი",
            region="Kvemo Kartli, Georgia",
            latitude=41.3322,
            longitude=44.2036,
            cultural_period="Lower Paleolithic (Oldowan / Mode 1)",
            chronology_bce="1,850,000 - 1,770,000 BP",
            source_archives=["Georgian National Museum Archives", "GNAS Reports"],
            metadata={
                "significance": "Earliest securely dated hominin fossils outside Africa (Homo georgicus)",
                "dating_method": "40Ar/39Ar and paleomagnetism (Matuyama-Olduvai)",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-GAD-002",
            name_en="Gadachrili Gora",
            name_ka="გადაჭრილი გორა",
            region="Kvemo Kartli, Georgia",
            latitude=41.4831,
            longitude=44.8194,
            cultural_period="Early Neolithic (Shulaveri-Shomu Culture)",
            chronology_bce="6000 - 5800 BCE",
            radiocarbon_samples=[
                RadiocarbonSample(
                    lab_code="RTD-7814",
                    bp_uncalibrated=7065,
                    std_dev=35,
                    material="Charred cereal grain (Triticum)",
                    calibrated_bce_range="6010 - 5880 cal BCE",
                )
            ],
            source_archives=["Georgian National Museum Archives", "PNAS 2017 Tartaric Acid Residue Catalog"],
            metadata={
                "significance": "Earliest biomolecular evidence of viniculture and ceramic wine jars (qvevri)",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-SAK-003",
            name_en="Sakdrisi-Kachagiani Gold Mine",
            name_ka="საყდრისი-ყაჩაღიანი",
            region="Kvemo Kartli, Georgia",
            latitude=41.4367,
            longitude=44.4178,
            cultural_period="Early Bronze Age (Kura-Araxes Culture)",
            chronology_bce="3350 - 2900 BCE",
            radiocarbon_samples=[
                RadiocarbonSample(
                    lab_code="Hd-24811",
                    bp_uncalibrated=4450,
                    std_dev=40,
                    material="Charcoal from fire-setting mining gallery",
                    calibrated_bce_range="3330 - 2930 cal BCE",
                )
            ],
            source_archives=["Georgian-German Mining Archaeology Reports", "GNM Metallurgy Collection"],
            metadata={
                "significance": "Prehistoric underground gold mining complex with stone hammers and fire-setting",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-TRI-004",
            name_en="Trialeti Barrow Cluster (Tsalka Plateau)",
            name_ka="თრიალეთის ყურგანები",
            region="Kvemo Kartli, Georgia",
            latitude=41.5983,
            longitude=44.0891,
            cultural_period="Middle Bronze Age (Trialeti-Vanadzor Culture)",
            chronology_bce="2100 - 1500 BCE",
            source_archives=["B.A. Kuftin Field Archives (1936-1940)", "Georgian National Museum"],
            metadata={
                "significance": "Monumental elite kurgans featuring silver and gold repousse goblets",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-VAN-005",
            name_en="Vani Sanctuary & City Site",
            name_ka="ვანის ნაქალაქარი",
            region="Imereti, Georgia",
            latitude=42.0856,
            longitude=42.5028,
            cultural_period="Late Bronze / Classical Colchian & Hellenistic",
            chronology_bce="800 - 50 BCE",
            source_archives=["O. Lordkipanidze Vani Expedition Archives", "Vani Archaeological Museum"],
            metadata={
                "significance": "Major religious and metallurgical center of ancient Colchis, Greek bronze & goldsmithing",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-ARM-006",
            name_en="Armazi Citadel (Bagineti)",
            name_ka="არმაზციხე (ბაგინეთი)",
            region="Mtskheta-Mtianeti, Georgia",
            latitude=41.8364,
            longitude=44.7219,
            cultural_period="Hellenistic / Early Iberian & Late Antique",
            chronology_bce="300 BCE - 400 CE",
            source_archives=["Mtskheta Archaeological Institute Reports", "Georgian Epigraphic Corpus"],
            metadata={
                "significance": "Royal acropolis of Iberia; locus of the Armazi Bilingual (Greek and Armazic Aramaic)",
            },
        ),
    ]


def export_geojson_collection(records: List[ArchaeologicalSiteRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    collection = {
        "type": "FeatureCollection",
        "metadata": {
            "project": "South Caucasus Open Archaeology Initiative (SCOAI)",
            "author": "Willi Ker",
            "license": "CC-BY-4.0",
        },
        "features": [record.to_geojson_feature() for record in records],
    }
    output_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    catalog = build_reference_catalog()
    for site in catalog:
        print(f"Initialized record: {site.site_id} ({site.name_en})")

    geojson_file = Path(__file__).parent / "data" / "sites.geojson"
    export_geojson_collection(catalog, geojson_file)
    print(f"Exported {len(catalog)} records to {geojson_file}")
