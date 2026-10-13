"""
Multilingual (Georgian/English) archival report parser and DMS coordinate converter
for South Caucasus archaeological publications. Includes structured extraction schema
builders for Gemini multimodal document workflows.
"""

import re
from typing import Any, Dict, List, Tuple
from scoai.radiocarbon import parse_archival_radiocarbon_line
from scoai.schema import ArchaeologicalSiteRecord, RadiocarbonSample


_DMS_REGEX = re.compile(
    r"(?P<deg>\d{2})\s*[°º]\s*"
    r"(?P<min>\d{1,2})\s*['′’]\s*"
    r"(?:(?P<sec>\d{1,2}(?:\.\d+)?)\s*[\"″”]\s*)?"
    r"(?P<hem>[NnSsEeWwჩსაღ]\.?\s*(?:გ\.?|გრ\.?)?)?"
)


def parse_dms_coordinate_pair(coord_text: str) -> Tuple[float, float]:
    """
    Converts legacy Georgian or English Degrees-Minutes-Seconds (DMS) coordinate
    strings into decimal WGS84 (latitude, longitude).

    Examples:
        "41°19'56\" N, 44°12'13\" E" -> (41.33222, 44.20361)
        "41°28'12\" ჩ.გ., 44°48'45\" ა.გ." -> (41.47, 44.8125)
    """
    matches = list(_DMS_REGEX.finditer(coord_text))
    if len(matches) < 2:
        raise ValueError(f"Expected a latitude/longitude DMS pair in: {coord_text!r}")

    coords: List[float] = []
    for m in matches[:2]:
        deg = float(m.group("deg"))
        minutes = float(m.group("min"))
        seconds = float(m.group("sec") or 0.0)
        decimal = deg + minutes / 60.0 + seconds / 3600.0
        hem = (m.group("hem") or "").strip().lower()
        if hem.startswith(("s", "w", "ს")):
            decimal = -decimal
        coords.append(round(decimal, 5))

    lat, lon = coords[0], coords[1]
    return lat, lon


def parse_archival_report_excerpt(excerpt: str, default_site_id: str = "GEO-ARC-001") -> ArchaeologicalSiteRecord:
    """
    Extracts an ArchaeologicalSiteRecord from a semi-structured Georgian/English archival report block
    containing site names, legacy DMS coordinates, cultural horizon, and 14C laboratory lines.
    """
    lines = [line.strip() for line in excerpt.strip().splitlines() if line.strip()]
    fields: Dict[str, str] = {}
    c14_samples: List[RadiocarbonSample] = []

    for line in lines:
        if ":" in line:
            key, val = line.split(":", 1)
            key_norm = key.strip().lower()
            if key_norm in ("site_id", "id", "კოდი"):
                fields["site_id"] = val.strip()
                continue
            elif key_norm in ("name_en", "site", "monument"):
                fields["name_en"] = val.strip()
                continue
            elif key_norm in ("name_ka", "ძეგლი", "სახელწოდება"):
                fields["name_ka"] = val.strip()
                continue
            elif key_norm in ("region", "მხარე", "რეგიონი"):
                fields["region"] = val.strip()
                continue
            elif key_norm in ("coordinates", "კოორდინატები"):
                fields["coordinates"] = val.strip()
                continue
            elif key_norm in ("period", "კულტურა", "პერიოდი"):
                fields["period"] = val.strip()
                continue
            elif key_norm in ("chronology", "ქრონოლოგია", "დათარიღება"):
                fields["chronology"] = val.strip()
                continue
            elif key_norm in ("source", "წყარო", "არქივი"):
                fields["source"] = val.strip()
                continue

        if any(tok in line for tok in ("±", "+/-", "+-")):
            try:
                c14_samples.append(parse_archival_radiocarbon_line(line))
            except ValueError:
                pass

    lat, lon = parse_dms_coordinate_pair(fields["coordinates"])
    record = ArchaeologicalSiteRecord(
        site_id=fields.get("site_id", default_site_id),
        name_en=fields.get("name_en", "Unknown Site"),
        name_ka=fields.get("name_ka"),
        region=fields.get("region", "Georgia"),
        latitude=lat,
        longitude=lon,
        cultural_period=fields.get("period", "Unclassified"),
        chronology_bce=fields.get("chronology", "Undated"),
        radiocarbon_samples=c14_samples,
        source_archives=[fields["source"]] if "source" in fields else [],
    )
    record.validate()
    return record


def build_gemini_extraction_payload(raw_archival_text: str) -> Dict[str, Any]:
    """
    Constructs the structured JSON-Schema extraction payload for Gemini 4 Argon
    to parse unindexed Georgian and multilingual archaeological monographs.
    """
    return {
        "model": "gemini-4-argon",
        "system_instruction": (
            "You are a computational archaeology extraction agent specializing in the South Caucasus. "
            "Extract archaeological site metadata, normalize legacy radiocarbon laboratory codes "
            "(Tb-, LE-, GIN-, IGAN-, RTD-), convert legacy DMS coordinates to decimal WGS84 within Georgia "
            "[lat 39.8..43.7, lon 39.9..46.8], and transliterate Asomtavruli/Mkhedruli epigraphy."
        ),
        "contents": raw_archival_text,
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "OBJECT",
            "required": [
                "site_id",
                "name_en",
                "region",
                "latitude",
                "longitude",
                "cultural_period",
                "chronology_bce",
                "radiocarbon_samples",
            ],
            "properties": {
                "site_id": {"type": "STRING"},
                "name_en": {"type": "STRING"},
                "name_ka": {"type": "STRING"},
                "region": {"type": "STRING"},
                "latitude": {"type": "NUMBER"},
                "longitude": {"type": "NUMBER"},
                "cultural_period": {"type": "STRING"},
                "chronology_bce": {"type": "STRING"},
                "radiocarbon_samples": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "required": ["lab_code", "bp_uncalibrated", "std_dev", "material"],
                        "properties": {
                            "lab_code": {"type": "STRING"},
                            "bp_uncalibrated": {"type": "INTEGER"},
                            "std_dev": {"type": "INTEGER"},
                            "material": {"type": "STRING"},
                            "context_stratum": {"type": "STRING"},
                        },
                    },
                },
            },
        },
    }
