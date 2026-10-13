"""
Statistical chronometric verification (Ward & Wilson 1978 chi-squared test)
and stratigraphic Law of Superposition checker for radiocarbon series.

Used by the SCOAI agentic workflow to detect OCR digit corruptions in legacy
radiocarbon tables and stratigraphic inversions across multi-layered tells.
"""

from dataclasses import dataclass, field
import math
import re
from typing import Dict, List, Optional, Tuple

from scoai.radiocarbon import calibrate_2sigma_bce
from scoai.schema import RadiocarbonSample


# Critical values of the chi-squared distribution at alpha = 0.05 for degrees of freedom 1..15
_CHI2_CRITICAL_005: Dict[int, float] = {
    1: 3.841,
    2: 5.991,
    3: 7.815,
    4: 9.488,
    5: 11.070,
    6: 12.592,
    7: 14.067,
    8: 15.507,
    9: 16.919,
    10: 18.307,
    11: 19.675,
    12: 21.026,
    13: 22.362,
    14: 23.685,
    15: 24.996,
}

_ROMAN_TO_INT: Dict[str, int] = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
}


@dataclass
class WardWilsonResult:
    """Result of the Ward & Wilson (1978) chi-squared test for combining radiocarbon dates."""

    sample_count: int
    degrees_of_freedom: int
    pooled_mean_bp: float
    pooled_std_bp: float
    pooled_calibrated_2sigma: str
    t_statistic: float
    critical_value_005: float
    is_coeval_at_95pct: bool
    outlier_lab_codes: List[str] = field(default_factory=list)


@dataclass
class StratigraphicAnomaly:
    """Represents a violation of the archaeological Law of Superposition between two strata."""

    upper_lab_code: str
    upper_stratum: str
    upper_bp: int
    lower_lab_code: str
    lower_stratum: str
    lower_bp: int
    inversion_magnitude_bp: int
    z_score: float
    diagnostic_message: str


def ward_wilson_chi2_test(samples: List[RadiocarbonSample]) -> WardWilsonResult:
    """
    Performs the Ward & Wilson (1978) test (Archaeometry 20(1): 19-31) to test whether
    a set of radiocarbon determinations from a single horizon or event are statistically
    consistent with a single pooled radiocarbon age:

        t_pooled = (sum(t_i / sigma_i^2)) / (sum(1 / sigma_i^2))
        T = sum((t_i - t_pooled)^2 / sigma_i^2) ~ chi^2(n - 1)
    """
    n = len(samples)
    if n == 0:
        raise ValueError("ward_wilson_chi2_test requires at least one RadiocarbonSample")
    if n == 1:
        s = samples[0]
        return WardWilsonResult(
            sample_count=1,
            degrees_of_freedom=0,
            pooled_mean_bp=float(s.bp_uncalibrated),
            pooled_std_bp=float(s.std_dev),
            pooled_calibrated_2sigma=s.calibrated_bce_range or calibrate_2sigma_bce(s.bp_uncalibrated, s.std_dev),
            t_statistic=0.0,
            critical_value_005=0.0,
            is_coeval_at_95pct=True,
            outlier_lab_codes=[],
        )

    weights = [1.0 / (s.std_dev**2) for s in samples]
    weight_sum = sum(weights)
    pooled_mean = sum(s.bp_uncalibrated * w for s, w in zip(samples, weights)) / weight_sum
    pooled_std = math.sqrt(1.0 / weight_sum)

    t_stat = sum(((s.bp_uncalibrated - pooled_mean) ** 2) / (s.std_dev**2) for s in samples)
    df = n - 1
    crit = _CHI2_CRITICAL_005.get(df, df + 2.0 * math.sqrt(2.0 * df))
    is_coeval = t_stat <= crit

    outliers: List[str] = []
    if not is_coeval:
        for s in samples:
            residual = abs(s.bp_uncalibrated - pooled_mean) / s.std_dev
            if residual > 2.0:
                outliers.append(s.lab_code)

    cal_pooled = calibrate_2sigma_bce(int(round(pooled_mean)), max(10, int(round(pooled_std))))
    return WardWilsonResult(
        sample_count=n,
        degrees_of_freedom=df,
        pooled_mean_bp=round(pooled_mean, 1),
        pooled_std_bp=round(pooled_std, 1),
        pooled_calibrated_2sigma=cal_pooled,
        t_statistic=round(t_stat, 3),
        critical_value_005=round(crit, 3),
        is_coeval_at_95pct=is_coeval,
        outlier_lab_codes=outliers,
    )


def extract_stratum_depth_index(context_stratum: Optional[str]) -> Optional[int]:
    """
    Extracts an ordinal depth index (1 = uppermost/youngest, higher = deeper/older)
    from English or Georgian stratigraphic labels such as:
        'Stratum III', 'Horizon V', 'ფენა III', 'Level 4'
    """
    if not context_stratum:
        return None
    match = re.search(
        r"\b(?:Stratum|Horizon|Layer|Level|Unit|ფენა|ჰორიზონტი)\s+([IVX]+|\d+)\b",
        context_stratum,
        re.IGNORECASE,
    )
    if not match:
        return None
    token = match.group(1).upper()
    if token in _ROMAN_TO_INT:
        return _ROMAN_TO_INT[token]
    if token.isdigit():
        return int(token)
    return None


def verify_stratigraphic_superposition(samples: List[RadiocarbonSample]) -> List[StratigraphicAnomaly]:
    """
    Verifies that radiocarbon ages respect the archaeological Law of Superposition:
    deeper strata (higher ordinal depth index, e.g., Stratum V) must not be statistically
    younger (> 2-sigma) than overlying strata (lower ordinal depth index, e.g., Stratum II).
    """
    indexed: List[Tuple[int, RadiocarbonSample]] = []
    for s in samples:
        idx = extract_stratum_depth_index(s.context_stratum)
        if idx is not None:
            indexed.append((idx, s))

    indexed.sort(key=lambda item: item[0])
    anomalies: List[StratigraphicAnomaly] = []

    for i in range(len(indexed)):
        upper_idx, upper_s = indexed[i]
        for j in range(i + 1, len(indexed)):
            lower_idx, lower_s = indexed[j]
            if lower_idx <= upper_idx:
                continue
            # Lower stratum should have >= BP than upper stratum
            diff_bp = upper_s.bp_uncalibrated - lower_s.bp_uncalibrated
            combined_sigma = math.sqrt(upper_s.std_dev**2 + lower_s.std_dev**2)
            z_score = diff_bp / combined_sigma if combined_sigma > 0 else 0.0
            if z_score > 2.0:
                msg = (
                    f"Stratigraphic inversion detected: deeper {lower_s.context_stratum} "
                    f"({lower_s.lab_code}: {lower_s.bp_uncalibrated} +/- {lower_s.std_dev} BP) is "
                    f"{diff_bp} yr younger (z={z_score:.1f}) than overlying {upper_s.context_stratum} "
                    f"({upper_s.lab_code}: {upper_s.bp_uncalibrated} +/- {upper_s.std_dev} BP). "
                    f"Suspected OCR leading-digit corruption in legacy table."
                )
                anomalies.append(
                    StratigraphicAnomaly(
                        upper_lab_code=upper_s.lab_code,
                        upper_stratum=upper_s.context_stratum or f"Stratum {upper_idx}",
                        upper_bp=upper_s.bp_uncalibrated,
                        lower_lab_code=lower_s.lab_code,
                        lower_stratum=lower_s.context_stratum or f"Stratum {lower_idx}",
                        lower_bp=lower_s.bp_uncalibrated,
                        inversion_magnitude_bp=diff_bp,
                        z_score=round(z_score, 2),
                        diagnostic_message=msg,
                    )
                )
    return anomalies
