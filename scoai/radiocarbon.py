"""
Radiocarbon (14C) normalization, Georgian/international laboratory code standardization,
and IntCal20 piecewise calibration curve approximation for South Caucasus archival records.
"""

import re
from typing import Dict, List, Tuple
from scoai.schema import RadiocarbonSample


# Mapping of Georgian and legacy transliterated laboratory prefixes to international standard codes (XRONOS / Radiocarbon)
LEGACY_LAB_PREFIX_MAP: Dict[str, str] = {
    "თბ": "Tb",
    "TB": "Tb",
    "Tb": "Tb",
    "tb": "Tb",
    "LE": "LE",
    "le": "LE",
    "GIN": "GIN",
    "gin": "GIN",
    "IGAN": "IGAN",
    "SOAN": "SOAN",
    "Ki": "Ki",
    "SPB": "SPb",
    "RTD": "RTD",
    "HD": "Hd",
    "Hd": "Hd",
    "OXA": "OxA",
    "OxA": "OxA",
    "GRA": "GrA",
    "GrA": "GrA",
    "MAMS": "MAMS",
    "BETA": "Beta",
    "Beta": "Beta",
    "AA": "AA",
    "UGAMS": "UGAMS",
}

LAB_INSTITUTION_METADATA: Dict[str, str] = {
    "Tb": "Tbilisi State University / Iv. Javakhishvili Radiocarbon Laboratory (Tbilisi, Georgia)",
    "LE": "Institute for the History of Material Culture (IIMK) Radiocarbon Laboratory",
    "GIN": "Geological Institute Radiocarbon Laboratory",
    "IGAN": "Institute of Geography Radiocarbon Laboratory",
    "RTD": "Weizmann Institute of Science Dangoor Research Accelerator Mass Spectrometer (Rehovot)",
    "Hd": "Heidelberg Academy of Sciences Radiocarbon Laboratory",
    "OxA": "Oxford Radiocarbon Accelerator Unit",
    "GrA": "Groningen AMS Facility",
    "MAMS": "Curt-Engelhorn-Zentrum Archaeometrie (Mannheim)",
    "UGAMS": "Center for Applied Isotope Studies, University of Georgia (Athens, USA)",
}

# Piecewise IntCal20 anchor points: (uncalibrated_14c_bp, calibrated_calendar_bp)
# Calendar BCE = calibrated_calendar_bp - 1950 (for calibrated_calendar_bp > 1950)
_INTCAL20_ANCHORS: List[Tuple[int, int]] = [
    (500, 525),
    (1000, 925),
    (1500, 1380),
    (2000, 1945),
    (2500, 2580),
    (3000, 3190),
    (3500, 3775),
    (4000, 4475),
    (4450, 5080),
    (5000, 5730),
    (5500, 6295),
    (6000, 6840),
    (6500, 7415),
    (7000, 7835),
    (7065, 7895),
    (7500, 8315),
    (8000, 8885),
    (8500, 9510),
    (9000, 10190),
    (10000, 11480),
    (12000, 13890),
    (15000, 18280),
    (20000, 24020),
    (25000, 29250),
    (30000, 34350),
    (35000, 39950),
]


def normalize_lab_code(raw_code: str) -> str:
    """Normalizes Georgian or inconsistent case lab prefixes to international standard notation."""
    cleaned = raw_code.strip().replace("–", "-").replace("—", "-").replace(" ", "")
    match = re.match(r"^([A-Za-zა-ჰ]+)-?(\d+[A-Za-z]?)$", cleaned)
    if not match:
        raise ValueError(f"Cannot parse laboratory code: {raw_code!r}")
    prefix_raw, number = match.groups()
    prefix = LEGACY_LAB_PREFIX_MAP.get(
        prefix_raw,
        LEGACY_LAB_PREFIX_MAP.get(prefix_raw.upper(), prefix_raw),
    )
    return f"{prefix}-{number}"


def _interpolate_cal_bp(c14_bp: float) -> float:
    """Piecewise linear interpolation over IntCal20 anchor nodes."""
    if c14_bp <= _INTCAL20_ANCHORS[0][0]:
        return c14_bp * (_INTCAL20_ANCHORS[0][1] / _INTCAL20_ANCHORS[0][0])
    if c14_bp >= _INTCAL20_ANCHORS[-1][0]:
        x0, y0 = _INTCAL20_ANCHORS[-2]
        x1, y1 = _INTCAL20_ANCHORS[-1]
        slope = (y1 - y0) / (x1 - x0)
        return y1 + (c14_bp - x1) * slope

    for i in range(len(_INTCAL20_ANCHORS) - 1):
        x0, y0 = _INTCAL20_ANCHORS[i]
        x1, y1 = _INTCAL20_ANCHORS[i + 1]
        if x0 <= c14_bp <= x1:
            t = (c14_bp - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return c14_bp


def calibrate_2sigma_bce(bp_uncalibrated: int, std_dev: int) -> str:
    """
    Computes an approximate 2-sigma (95.4%) calibrated calendar interval
    using IntCal20 anchor interpolation and error propagation.
    """
    effective_sigma = (std_dev**2 + 25**2) ** 0.5
    high_c14 = bp_uncalibrated + 1.96 * effective_sigma
    low_c14 = max(100.0, bp_uncalibrated - 1.96 * effective_sigma)

    cal_bp_older = _interpolate_cal_bp(high_c14)
    cal_bp_younger = _interpolate_cal_bp(low_c14)

    older_bce = int(round((cal_bp_older - 1950) / 10.0) * 10)
    younger_bce = int(round((cal_bp_younger - 1950) / 10.0) * 10)

    if older_bce > 0 and younger_bce > 0:
        return f"{older_bce} - {younger_bce} cal BCE"
    elif older_bce > 0 and younger_bce <= 0:
        return f"{older_bce} cal BCE - {abs(younger_bce)} cal CE"
    else:
        return f"{abs(older_bce)} - {abs(younger_bce)} cal CE"


_GEORGIAN_MATERIAL_MAP: Dict[str, str] = {
    "ნახშირი": "Charcoal",
    "ხის ნახშირი": "Charcoal",
    "ძვალი": "Bone collagen",
    "მარცვალი": "Charred cereal grain",
    "ხორბალი": "Charred Triticum grain",
    "ქერი": "Charred Hordeum grain",
    "ყურძნის წიპწა": "Vitis vinifera pip",
    "ხე": "Wood",
}


def parse_archival_radiocarbon_line(text: str) -> RadiocarbonSample:
    """
    Parses a raw Georgian or English archival radiocarbon string into a
    normalized RadiocarbonSample with automatic IntCal20 2-sigma calibration.

    Examples:
        "თბ-312: 6850 ± 70 BP (ნახშირი, ფენა III)"
        "TB-294: 6610+-75 BP (Charcoal, Building IV)"
        "RTD-7814: 7065 ± 35 BP (Charred Triticum grain)"
    """
    pattern = re.compile(
        r"(?P<code>[A-Za-zა-ჰ]{2,6}\s*[-–—]\s*\d+[A-Za-z]?)"
        r"[\s:;,\(\[]+"
        r"(?P<bp>\d{3,5})\s*(?:±|\+/-|\+-)\s*(?P<std>\d{1,4})"
        r"\s*(?:BP|bp|წ\.?\s*წ\.?)?"
        r"(?:\s*\((?P<meta>[^)]+)\))?"
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Could not extract radiocarbon record from archival text: {text!r}")

    lab_code = normalize_lab_code(match.group("code"))
    bp = int(match.group("bp"))
    std = int(match.group("std"))
    meta_raw = (match.group("meta") or "Charcoal").strip()

    parts = [p.strip() for p in meta_raw.split(",")]
    raw_material = parts[0]
    material_en = _GEORGIAN_MATERIAL_MAP.get(raw_material, raw_material)
    context_stratum = ", ".join(parts[1:]) if len(parts) > 1 else None

    cal_range = calibrate_2sigma_bce(bp, std)
    sample = RadiocarbonSample(
        lab_code=lab_code,
        bp_uncalibrated=bp,
        std_dev=std,
        material=material_en,
        calibrated_bce_range=cal_range,
        context_stratum=context_stratum,
    )
    sample.validate()
    return sample
