"""
Core data schemas and spatial-chronometric validators for the South Caucasus Open Archaeology Initiative.
"""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


# Bounding box covering Georgia and adjacent South Caucasus border zones (WGS84)
CAUCASUS_LAT_MIN = 39.8
CAUCASUS_LAT_MAX = 43.7
CAUCASUS_LON_MIN = 39.9
CAUCASUS_LON_MAX = 46.8


@dataclass
class RadiocarbonSample:
    """Normalized radiocarbon (14C) sample record compatible with XRONOS schema."""

    lab_code: str  # e.g., "Tb-312", "LE-1425", "RTD-7814", "GIN-2940"
    bp_uncalibrated: int  # Uncalibrated radiocarbon age in years BP (before 1950)
    std_dev: int  # 1-sigma laboratory uncertainty in years
    material: str  # Sampled material (charcoal, bone collagen, charred grain, wood)
    calibrated_bce_range: Optional[str] = None  # Calibrated 2-sigma (95.4%) range
    context_stratum: Optional[str] = None
    delta_c13_permil: Optional[float] = None

    def validate(self) -> None:
        if not self.lab_code or "-" not in self.lab_code:
            raise ValueError(f"Invalid radiocarbon lab_code format: {self.lab_code!r}")
        if not (100 <= self.bp_uncalibrated <= 55000):
            raise ValueError(f"Uncalibrated BP out of radiocarbon range (100..55000): {self.bp_uncalibrated}")
        if not (5 <= self.std_dev <= 2000):
            raise ValueError(f"Standard deviation out of expected range (5..2000): {self.std_dev}")


@dataclass
class EpigraphicInscription:
    """Structured record of an ancient or medieval epigraphic monument."""

    inscription_id: str
    site_id: str
    script: str  # e.g., "Asomtavruli", "Armazic Aramaic", "Ancient Greek"
    language: str
    original_text: str
    mkhedruli_transliteration: Optional[str] = None
    latin_transliteration: Optional[str] = None
    translation_en: Optional[str] = None
    dating_str: str = ""
    reference: str = ""


@dataclass
class ArchaeologicalSiteRecord:
    """Standardized geocoded archaeological site record for the South Caucasus."""

    site_id: str
    name_en: str
    name_ka: Optional[str]
    region: str
    latitude: float
    longitude: float
    cultural_period: str
    chronology_bce: str
    elevation_m: Optional[int] = None
    radiocarbon_samples: List[RadiocarbonSample] = field(default_factory=list)
    inscriptions: List[EpigraphicInscription] = field(default_factory=list)
    source_archives: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.site_id.startswith("GEO-"):
            raise ValueError(f"Site ID must start with 'GEO-': {self.site_id}")
        if not (CAUCASUS_LAT_MIN <= self.latitude <= CAUCASUS_LAT_MAX):
            raise ValueError(
                f"Latitude {self.latitude} for {self.site_id} outside South Caucasus bounds "
                f"[{CAUCASUS_LAT_MIN}, {CAUCASUS_LAT_MAX}]"
            )
        if not (CAUCASUS_LON_MIN <= self.longitude <= CAUCASUS_LON_MAX):
            raise ValueError(
                f"Longitude {self.longitude} for {self.site_id} outside South Caucasus bounds "
                f"[{CAUCASUS_LON_MIN}, {CAUCASUS_LON_MAX}]"
            )
        for sample in self.radiocarbon_samples:
            sample.validate()

    def to_geojson_feature(self) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(self.longitude, 5), round(self.latitude, 5)],
            },
            "properties": {
                "site_id": self.site_id,
                "name_en": self.name_en,
                "name_ka": self.name_ka,
                "region": self.region,
                "elevation_m": self.elevation_m,
                "cultural_period": self.cultural_period,
                "chronology_bce": self.chronology_bce,
                "radiocarbon_count": len(self.radiocarbon_samples),
                "radiocarbon_samples": [asdict(s) for s in self.radiocarbon_samples],
                "inscriptions": [asdict(i) for i in self.inscriptions],
                "sources": self.source_archives,
                "metadata": self.metadata,
            },
        }
