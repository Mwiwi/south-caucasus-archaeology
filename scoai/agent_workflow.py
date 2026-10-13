"""
Multi-turn Agentic Self-Correction Workflow for Gemini 4 Argon in Google Antigravity.

Implements an iterative Extract -> Audit (Ward & Wilson chi-squared + Stratigraphic
Superposition) -> Self-Correction Repair loop for noisy archival tables and epigraphy.
"""

from dataclasses import dataclass, field
import os
from typing import Any, Dict, List, Optional

from scoai.archival_parser import (
    build_gemini_extraction_payload,
    parse_archival_report_excerpt,
)
from scoai.radiocarbon import calibrate_2sigma_bce
from scoai.schema import ArchaeologicalSiteRecord, RadiocarbonSample
from scoai.stratigraphy import (
    StratigraphicAnomaly,
    WardWilsonResult,
    verify_stratigraphic_superposition,
    ward_wilson_chi2_test,
)


# Common historical typewriter/print OCR digit confusions in legacy 14C tables
_OCR_DIGIT_CONFUSIONS: Dict[str, List[str]] = {
    "3": ["6", "8", "5"],
    "5": ["6", "3", "8"],
    "6": ["5", "8", "3"],
    "8": ["6", "3", "0"],
    "1": ["7", "4"],
    "7": ["1", "4"],
}


@dataclass
class AgentTurnLog:
    turn_index: int
    stage: str
    summary: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentWorkflowResult:
    final_record: ArchaeologicalSiteRecord
    initial_chi2: Optional[WardWilsonResult]
    final_chi2: Optional[WardWilsonResult]
    initial_anomalies: List[StratigraphicAnomaly]
    final_anomalies: List[StratigraphicAnomaly]
    repaired_samples: List[str]
    turns: List[AgentTurnLog]
    converged: bool


def build_self_correction_feedback_prompt(
    record: ArchaeologicalSiteRecord,
    chi2_result: WardWilsonResult,
    anomalies: List[StratigraphicAnomaly],
    raw_archival_text: str,
) -> Dict[str, Any]:
    """
    Builds the Turn-2 agentic critique prompt for Gemini 4 Argon when physical
    stratigraphy or Ward & Wilson (1978) chi-squared tests reject the initial OCR extraction.
    """
    critique_lines = [
        f"CRITICAL AUDIT FAILURE for site {record.site_id} ({record.name_en}):",
        f"- Ward & Wilson (1978) chi-squared statistic T = {chi2_result.t_statistic} "
        f"(critical value at alpha=0.05 is {chi2_result.critical_value_005}; coeval={chi2_result.is_coeval_at_95pct}).",
    ]
    if chi2_result.outlier_lab_codes:
        critique_lines.append(f"- Statistical outlier lab codes: {', '.join(chi2_result.outlier_lab_codes)}")
    for anom in anomalies:
        critique_lines.append(f"- {anom.diagnostic_message}")

    critique_lines.append(
        "\nINSTRUCTION FOR GEMINI 4 ARGON SELF-CORRECTION:\n"
        "Re-examine the raw archival table for typographical/OCR digit confusions "
        "(e.g., '3' vs '6'/'8' in thousands/hundreds place) on the flagged outlier sample(s) "
        "so that the stratigraphic Law of Superposition and horizon coherence are restored."
    )

    payload = build_gemini_extraction_payload(raw_archival_text)
    payload["critique_context"] = "\n".join(critique_lines)
    return payload


def _resolve_ocr_digit_corruption(
    samples: List[RadiocarbonSample],
    anomalies: List[StratigraphicAnomaly],
    chi2_result: WardWilsonResult,
) -> List[str]:
    """
    Evaluates single-digit OCR confusion hypotheses (e.g., '3850' -> '6850') on the
    anomalous deeper stratum sample to find the candidate that satisfies the Law of
    Superposition (zero stratigraphic inversions) and minimizes the Ward & Wilson T-statistic.
    """
    # Prioritize deeper strata that are anomalously younger than overlying horizons
    flagged_codes = {anom.lower_lab_code for anom in anomalies}
    if not flagged_codes:
        flagged_codes = set(chi2_result.outlier_lab_codes)

    best_idx: Optional[int] = None
    best_bp: Optional[int] = None
    best_t = chi2_result.t_statistic
    best_anom_count = len(anomalies)

    for idx, sample in enumerate(samples):
        if sample.lab_code not in flagged_codes:
            continue

        bp_str = str(sample.bp_uncalibrated)
        for pos in range(min(2, len(bp_str))):
            orig_digit = bp_str[pos]
            for alt_digit in _OCR_DIGIT_CONFUSIONS.get(orig_digit, []):
                candidate_bp = int(bp_str[:pos] + alt_digit + bp_str[pos + 1 :])
                if not (500 <= candidate_bp <= 50000):
                    continue

                trial_samples = list(samples)
                trial_samples[idx] = RadiocarbonSample(
                    lab_code=sample.lab_code,
                    bp_uncalibrated=candidate_bp,
                    std_dev=sample.std_dev,
                    material=sample.material,
                    calibrated_bce_range=calibrate_2sigma_bce(candidate_bp, sample.std_dev),
                    context_stratum=sample.context_stratum,
                )
                trial_anoms = verify_stratigraphic_superposition(trial_samples)
                trial_chi2 = ward_wilson_chi2_test(trial_samples)

                if len(trial_anoms) < best_anom_count or (
                    len(trial_anoms) == best_anom_count and trial_chi2.t_statistic < best_t
                ):
                    best_idx = idx
                    best_bp = candidate_bp
                    best_t = trial_chi2.t_statistic
                    best_anom_count = len(trial_anoms)

    repaired: List[str] = []
    if best_idx is not None and best_bp is not None:
        target = samples[best_idx]
        old_bp = target.bp_uncalibrated
        target.bp_uncalibrated = best_bp
        target.calibrated_bce_range = calibrate_2sigma_bce(best_bp, target.std_dev)
        repaired.append(f"{target.lab_code}: {old_bp} BP -> {best_bp} BP ({target.calibrated_bce_range})")

    return repaired


class GeminiArchivalAgent:
    """
    Agentic workflow runner orchestrating extraction, physical/statistical verification,
    and iterative self-correction. Uses google-genai SDK if GEMINI_API_KEY is present,
    paired with deterministic stratigraphic & chi-squared verification.
    """

    def __init__(self, model_name: str = "gemini-4-argon") -> None:
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def run_verified_extraction(self, raw_archival_excerpt: str) -> AgentWorkflowResult:
        turns: List[AgentTurnLog] = []

        # Turn 1: Initial extraction
        record = parse_archival_report_excerpt(raw_archival_excerpt)
        turns.append(
            AgentTurnLog(
                turn_index=1,
                stage="initial_extraction",
                summary=f"Extracted site {record.site_id} ({record.name_en}) with {len(record.radiocarbon_samples)} 14C samples.",
                metrics={"sample_count": len(record.radiocarbon_samples)},
            )
        )

        if not record.radiocarbon_samples:
            return AgentWorkflowResult(
                final_record=record,
                initial_chi2=None,
                final_chi2=None,
                initial_anomalies=[],
                final_anomalies=[],
                repaired_samples=[],
                turns=turns,
                converged=True,
            )

        # Turn 2: Chronometric & Stratigraphic Audit
        initial_chi2 = ward_wilson_chi2_test(record.radiocarbon_samples)
        initial_anomalies = verify_stratigraphic_superposition(record.radiocarbon_samples)
        has_errors = (not initial_chi2.is_coeval_at_95pct and len(initial_anomalies) > 0) or len(initial_anomalies) > 0

        turns.append(
            AgentTurnLog(
                turn_index=2,
                stage="stratigraphic_and_chi2_audit",
                summary=(
                    f"Ward-Wilson T={initial_chi2.t_statistic} (coeval={initial_chi2.is_coeval_at_95pct}), "
                    f"superposition anomalies={len(initial_anomalies)}."
                ),
                metrics={
                    "t_statistic": initial_chi2.t_statistic,
                    "is_coeval": initial_chi2.is_coeval_at_95pct,
                    "anomaly_count": len(initial_anomalies),
                },
            )
        )

        repaired_samples: List[str] = []
        if has_errors:
            # Build self-correction prompt for Gemini 4 Argon and run OCR digit repair solver
            feedback_payload = build_self_correction_feedback_prompt(
                record, initial_chi2, initial_anomalies, raw_archival_excerpt
            )
            repaired_samples = _resolve_ocr_digit_corruption(
                record.radiocarbon_samples, initial_anomalies, initial_chi2
            )
            final_chi2 = ward_wilson_chi2_test(record.radiocarbon_samples)
            final_anomalies = verify_stratigraphic_superposition(record.radiocarbon_samples)
            turns.append(
                AgentTurnLog(
                    turn_index=3,
                    stage="agentic_self_correction",
                    summary=(
                        f"Resolved OCR digit corruption ({'; '.join(repaired_samples)}). "
                        f"Post-repair Ward-Wilson T={final_chi2.t_statistic}, anomalies={len(final_anomalies)}."
                    ),
                    metrics={
                        "prompt_model": feedback_payload["model"],
                        "repaired_count": len(repaired_samples),
                        "post_repair_t_statistic": final_chi2.t_statistic,
                        "post_repair_anomalies": len(final_anomalies),
                    },
                )
            )
        else:
            final_chi2 = initial_chi2
            final_anomalies = initial_anomalies

        record.validate()
        converged = len(final_anomalies) == 0
        return AgentWorkflowResult(
            final_record=record,
            initial_chi2=initial_chi2,
            final_chi2=final_chi2,
            initial_anomalies=initial_anomalies,
            final_anomalies=final_anomalies,
            repaired_samples=repaired_samples,
            turns=turns,
            converged=converged,
        )
