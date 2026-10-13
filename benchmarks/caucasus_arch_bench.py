"""
CaucasusArch-Bench: Domain-Specific Evaluation Benchmark for Multimodal & Agentic
Workflows in South Caucasus Computational Archaeology.

Evaluates:
1. Agentic detection & self-correction of OCR digit corruptions in legacy 14C tables
   via Ward & Wilson (1978) chi-squared and stratigraphic superposition constraints.
2. Multi-sample Bayesian/Ward-Wilson phase pooling on Bronze Age kurgan horizons.
3. Old Georgian Asomtavruli and Nuskhuri epigraphic decoding & ejective-preserving
   scholarly Kartvelological transliteration.
4. Cross-lingual Georgian/English archival DMS coordinate & 14C record extraction.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List

from scoai.agent_workflow import GeminiArchivalAgent
from scoai.archival_parser import parse_archival_report_excerpt
from scoai.catalog import build_reference_catalog
from scoai.epigraphy import (
    asomtavruli_to_mkhedruli,
    mkhedruli_to_nuskhuri,
    transliterate_georgian_to_latin,
)
from scoai.stratigraphy import ward_wilson_chi2_test


@dataclass
class BenchmarkTaskResult:
    task_id: str
    category: str
    description: str
    passed: bool
    metrics: Dict[str, Any]


NOISY_OCR_EXCERPT_KDG = """
კოდი: GEO-KDG-007
Name_EN: Khramis Didi-Gora
ძეგლი: ხრამის დიდი გორა
მხარე: Kvemo Kartli, Georgia
კოორდინატები: 41°23'28" ჩ.გ., 44°54'44" ა.გ.
კულტურა: Early Neolithic (Shulaveri-Shomu Culture)
ქრონოლოგია: 5850 - 5400 cal BCE
წყარო: Georgian State Museum Kvemo Kartli Monograph Series

რადიოკარბონული თარიღები (Noisy OCR scan with leading-digit corruption in Stratum III):
1. LE-1340: 6540 ± 80 BP (მარცვალი, Stratum II)
2. თბ-312: 3850 ± 70 BP (ნახშირი, Stratum III)
""".strip()


def run_caucasus_arch_benchmark(output_json_path: Path | None = None, verbose: bool = True) -> List[BenchmarkTaskResult]:
    results: List[BenchmarkTaskResult] = []
    catalog = {s.site_id: s for s in build_reference_catalog()}

    # Task 1: Agentic OCR Corruption Detection & Self-Correction Loop
    agent = GeminiArchivalAgent(model_name="gemini-4-argon")
    wf_res = agent.run_verified_extraction(NOISY_OCR_EXCERPT_KDG)
    tb312_after = next(s for s in wf_res.final_record.radiocarbon_samples if s.lab_code == "Tb-312")
    task1_passed = (
        len(wf_res.initial_anomalies) == 1
        and len(wf_res.final_anomalies) == 0
        and tb312_after.bp_uncalibrated == 6850
        and wf_res.converged
    )
    results.append(
        BenchmarkTaskResult(
            task_id="BENCH-C14-OCR-01",
            category="Agentic Stratigraphic Self-Correction",
            description="Detect & repair OCR digit confusion (3850 -> 6850 BP) violating Law of Superposition in Stratum III",
            passed=task1_passed,
            metrics={
                "initial_t_statistic": wf_res.initial_chi2.t_statistic if wf_res.initial_chi2 else None,
                "initial_superposition_z": wf_res.initial_anomalies[0].z_score if wf_res.initial_anomalies else 0.0,
                "repaired_samples": wf_res.repaired_samples,
                "final_t_statistic": wf_res.final_chi2.t_statistic if wf_res.final_chi2 else None,
                "agent_turns": len(wf_res.turns),
            },
        )
    )

    # Task 2: Ward & Wilson (1978) Phase Pooling on Ananauri Big Kurgan No. 3
    ananauri = catalog["GEO-ANA-013"]
    chi2_ana = ward_wilson_chi2_test(ananauri.radiocarbon_samples)
    task2_passed = (
        chi2_ana.is_coeval_at_95pct
        and chi2_ana.t_statistic < chi2_ana.critical_value_005
        and 3895.0 <= chi2_ana.pooled_mean_bp <= 3915.0
    )
    results.append(
        BenchmarkTaskResult(
            task_id="BENCH-STRAT-ANA-02",
            category="Chronometric Phase Pooling (Ward & Wilson 1978)",
            description="Verify single-event burial wagon construction coevality for Ananauri Big Kurgan No. 3",
            passed=task2_passed,
            metrics={
                "pooled_mean_bp": chi2_ana.pooled_mean_bp,
                "pooled_std_bp": chi2_ana.pooled_std_bp,
                "pooled_2sigma_cal": chi2_ana.pooled_calibrated_2sigma,
                "t_statistic": chi2_ana.t_statistic,
                "critical_005": chi2_ana.critical_value_005,
                "is_coeval_95pct": chi2_ana.is_coeval_at_95pct,
            },
        )
    )

    # Task 3: Bolnisi Sioni (494 CE) Asomtavruli Paleography & Scholarly Transliteration
    bolnisi_inscr = catalog["GEO-BOL-019"].inscriptions[0]
    expected_mkh = "ქე დათუნა ეპისკოპოსსა კრებულითურთ ამის ეკლესიისაყ"
    expected_lat = "ke datuna ep'isk'op'ossa k'rebuliturt amis ek'lesiisaq'"
    task3_passed = (
        bolnisi_inscr.mkhedruli_transliteration == expected_mkh
        and bolnisi_inscr.latin_transliteration == expected_lat
    )
    results.append(
        BenchmarkTaskResult(
            task_id="BENCH-EPI-BOL-03",
            category="Ancient Epigraphy (Asomtavruli -> Kartvelological Latin)",
            description="Decode 5th-century Bolnisi Sioni Asomtavruli inscription preserving ejective stops (p', k', q')",
            passed=task3_passed,
            metrics={
                "source_script": "Asomtavruli (U+10A0..U+10C5)",
                "mkhedruli": bolnisi_inscr.mkhedruli_transliteration,
                "scholarly_latin": bolnisi_inscr.latin_transliteration,
            },
        )
    )

    # Task 4: Mtskheta Jvari Trilinear Script Conversion (Asomtavruli <-> Nuskhuri <-> Mkhedruli)
    jvari_inscr = catalog["GEO-JVR-020"].inscriptions[0]
    nuskhuri_text = mkhedruli_to_nuskhuri(jvari_inscr.original_text)
    roundtrip_mkh = asomtavruli_to_mkhedruli(nuskhuri_text)
    task4_passed = (
        roundtrip_mkh == jvari_inscr.mkhedruli_transliteration
        and "demet'res up'at'ossa" in (jvari_inscr.latin_transliteration or "")
    )
    results.append(
        BenchmarkTaskResult(
            task_id="BENCH-EPI-JVR-04",
            category="Ecclesiastical Script Roundtrip (Asomtavruli/Nuskhuri)",
            description="Convert Mtskheta Jvari relief of Demetre the Hypatos across Asomtavruli, Nuskhuri, and Mkhedruli",
            passed=task4_passed,
            metrics={
                "nuskhuri_sample": nuskhuri_text[:28],
                "latin_excerpt": transliterate_georgian_to_latin(roundtrip_mkh),
            },
        )
    )

    # Task 5: Multilingual Georgian/English Archival DMS & Lab Code Extraction
    sample_file = Path(__file__).parent.parent / "data" / "raw_samples" / "kvemo_kartli_archival_sample.txt"
    imiris_rec = parse_archival_report_excerpt(sample_file.read_text(encoding="utf-8"))
    chi2_imiris = ward_wilson_chi2_test(imiris_rec.radiocarbon_samples)
    task5_passed = (
        imiris_rec.site_id == "GEO-IMR-021"
        and len(imiris_rec.radiocarbon_samples) == 2
        and chi2_imiris.is_coeval_at_95pct
    )
    results.append(
        BenchmarkTaskResult(
            task_id="BENCH-GEO-IMR-05",
            category="Cross-Lingual Archival Parsing & Geodesy",
            description="Extract Georgian DMS coordinates, normalize თბ-29 -> Tb-29, and verify Neolithic horizon coevality",
            passed=task5_passed,
            metrics={
                "site_id": imiris_rec.site_id,
                "decimal_wgs84": [imiris_rec.latitude, imiris_rec.longitude],
                "ward_wilson_t": chi2_imiris.t_statistic,
                "pooled_cal_bce": chi2_imiris.pooled_calibrated_2sigma,
            },
        )
    )

    if output_json_path is not None:
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "benchmark": "CaucasusArch-Bench v0.2.0",
            "target_model": "gemini-4-argon",
            "total_tasks": len(results),
            "passed_tasks": sum(1 for r in results if r.passed),
            "pass_rate": round(sum(1 for r in results if r.passed) / len(results), 4),
            "tasks": [asdict(r) for r in results],
        }
        output_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if verbose:
        passed_count = sum(1 for r in results if r.passed)
        print(f"\n=== CaucasusArch-Bench Evaluation Suite ({passed_count}/{len(results)} Passed) ===")
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.task_id} ({r.category}): {r.description}")

    return results


if __name__ == "__main__":
    out_file = Path(__file__).parent.parent / "data" / "caucasus_arch_bench_results.json"
    run_caucasus_arch_benchmark(output_json_path=out_file, verbose=True)
