"""
Automated test suite for the South Caucasus Open Archaeology Initiative (SCOAI).
Run with: python3 -m unittest discover -s tests -v  (or pytest)
"""

from pathlib import Path
import tempfile
import unittest

from scoai.archival_parser import (
    build_gemini_extraction_payload,
    parse_archival_report_excerpt,
    parse_dms_coordinate_pair,
)
from scoai.catalog import build_reference_catalog
from scoai.epigraphy import (
    asomtavruli_to_mkhedruli,
    mkhedruli_to_asomtavruli,
    mkhedruli_to_nuskhuri,
    transliterate_georgian_to_latin,
)
from scoai.exporters import (
    export_geojson_collection,
    export_pelagios_jsonld,
    export_xronos_csv,
    find_nearest_neighbors,
    haversine_km,
)
from scoai.radiocarbon import (
    calibrate_2sigma_bce,
    normalize_lab_code,
    parse_archival_radiocarbon_line,
)


class TestRadiocarbonNormalization(unittest.TestCase):
    def test_legacy_lab_prefix_normalization(self) -> None:
        self.assertEqual(normalize_lab_code("თბ-312"), "Tb-312")
        self.assertEqual(normalize_lab_code("TB-78"), "Tb-78")
        self.assertEqual(normalize_lab_code("LE-1425"), "LE-1425")
        self.assertEqual(normalize_lab_code("GIN-2940"), "GIN-2940")
        self.assertEqual(normalize_lab_code("RTD-7814"), "RTD-7814")

    def test_parse_archival_radiocarbon_line_georgian(self) -> None:
        raw = "თბ-312: 6850 ± 70 BP (ნახშირი, ფენა III)"
        sample = parse_archival_radiocarbon_line(raw)
        self.assertEqual(sample.lab_code, "Tb-312")
        self.assertEqual(sample.bp_uncalibrated, 6850)
        self.assertEqual(sample.std_dev, 70)
        self.assertEqual(sample.material, "Charcoal")
        self.assertEqual(sample.context_stratum, "ფენა III")
        self.assertIn("cal BCE", sample.calibrated_bce_range or "")

    def test_intcal20_calibration_neolithic_shulaveri(self) -> None:
        cal = calibrate_2sigma_bce(7065, 35)
        self.assertTrue(cal.endswith("cal BCE"))
        parts = cal.replace("cal BCE", "").split("-")
        older, younger = int(parts[0].strip()), int(parts[1].strip())
        self.assertGreaterEqual(older, 5950)
        self.assertLessEqual(younger, 5900)


class TestEpigraphyEngine(unittest.TestCase):
    def test_asomtavruli_mkhedruli_roundtrip(self) -> None:
        bolnisi_fragment = "ႵႤ ႣႠႧႳႬႠ ႤႮႨႱႩႭႮႭႱႱႠ"
        mkh = asomtavruli_to_mkhedruli(bolnisi_fragment)
        self.assertEqual(mkh, "ქე დათუნა ეპისკოპოსსა")
        self.assertEqual(mkhedruli_to_asomtavruli(mkh), bolnisi_fragment)

    def test_nuskhuri_conversion_and_scholarly_latin(self) -> None:
        word_mkh = "საქართველო"
        nus = mkhedruli_to_nuskhuri(word_mkh)
        self.assertEqual(asomtavruli_to_mkhedruli(nus), word_mkh)
        latin = transliterate_georgian_to_latin(word_mkh)
        self.assertEqual(latin, "sakartvelo")

    def test_ejective_distinctions_in_scholarly_latin(self) -> None:
        # კ (k') vs ქ (k), წ (ts') vs ც (ts), ყ (q')
        self.assertEqual(transliterate_georgian_to_latin("კოლხეთი"), "k'olkheti")
        self.assertEqual(transliterate_georgian_to_latin("საყდრისი"), "saq'drisi")


class TestArchivalParserAndCatalog(unittest.TestCase):
    def test_dms_coordinate_conversion(self) -> None:
        lat, lon = parse_dms_coordinate_pair('41°19\'56" ჩ.გ., 44°12\'13" ა.გ.')
        self.assertAlmostEqual(lat, 41.33222, places=4)
        self.assertAlmostEqual(lon, 44.20361, places=4)

    def test_parse_multilingual_archival_sample_file(self) -> None:
        sample_path = (
            Path(__file__).parent.parent / "data" / "raw_samples" / "kvemo_kartli_archival_sample.txt"
        )
        excerpt = sample_path.read_text(encoding="utf-8")
        record = parse_archival_report_excerpt(excerpt)
        self.assertEqual(record.site_id, "GEO-IMR-021")
        self.assertEqual(record.name_en, "Imiris Gora")
        self.assertEqual(record.name_ka, "იმირის გორა")
        self.assertEqual(len(record.radiocarbon_samples), 2)
        self.assertEqual(record.radiocarbon_samples[0].lab_code, "Tb-29")
        self.assertEqual(record.radiocarbon_samples[1].lab_code, "LE-1060")

    def test_gemini_extraction_payload_schema(self) -> None:
        payload = build_gemini_extraction_payload("Sample text")
        self.assertEqual(payload["model"], "gemini-4-argon")
        self.assertIn("radiocarbon_samples", payload["response_schema"]["properties"])

    def test_reference_catalog_and_exporters(self) -> None:
        catalog = build_reference_catalog()
        self.assertEqual(len(catalog), 20)
        for site in catalog:
            site.validate()

        gad = next(s for s in catalog if s.site_id == "GEO-GAD-005")
        shu = next(s for s in catalog if s.site_id == "GEO-SHU-006")
        dist = haversine_km(gad.latitude, gad.longitude, shu.latitude, shu.longitude)
        self.assertLess(dist, 2.0)

        neighbors = find_nearest_neighbors(gad, catalog, top_k=1)
        self.assertEqual(neighbors[0][0], "GEO-SHU-006")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            geojson_p = tmp_dir / "sites.geojson"
            jsonld_p = tmp_dir / "sites_pelagios.jsonld"
            xronos_p = tmp_dir / "radiocarbon_xronos.csv"

            export_geojson_collection(catalog, geojson_p)
            export_pelagios_jsonld(catalog, jsonld_p)
            rows = export_xronos_csv(catalog, xronos_p)

            self.assertTrue(geojson_p.exists())
            self.assertTrue(jsonld_p.exists())
            self.assertTrue(xronos_p.exists())
            self.assertGreaterEqual(rows, 25)


if __name__ == "__main__":
    unittest.main()
