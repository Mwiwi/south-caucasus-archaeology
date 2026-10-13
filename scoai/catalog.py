"""
Reference catalog of 20 major archaeological and epigraphic sites across Georgia,
spanning the Lower Paleolithic, Upper Paleolithic, Neolithic (Shulaveri-Shomu),
Chalcolithic/Early Bronze Age (Kura-Araxes), Middle Bronze Age (Trialeti/Bedeni),
Late Bronze/Colchian Antiquity, and Early Christian/Iberian Epigraphy.
"""

from typing import List
from scoai.epigraphy import enrich_inscription
from scoai.radiocarbon import calibrate_2sigma_bce
from scoai.schema import ArchaeologicalSiteRecord, RadiocarbonSample


def _c14(
    lab_code: str,
    bp: int,
    std: int,
    material: str,
    context: str,
    cal_override: str = "",
) -> RadiocarbonSample:
    return RadiocarbonSample(
        lab_code=lab_code,
        bp_uncalibrated=bp,
        std_dev=std,
        material=material,
        calibrated_bce_range=cal_override or calibrate_2sigma_bce(bp, std),
        context_stratum=context,
    )


def build_reference_catalog() -> List[ArchaeologicalSiteRecord]:
    """Returns 20 validated archaeological site records across Georgia."""
    return [
        # --- PALEOLITHIC ---
        ArchaeologicalSiteRecord(
            site_id="GEO-DMN-001",
            name_en="Dmanisi Hominin Site",
            name_ka="დმანისის ნაქალაქარი",
            region="Kvemo Kartli, Georgia",
            latitude=41.3322,
            longitude=44.2036,
            elevation_m=910,
            cultural_period="Lower Paleolithic (Oldowan / Mode 1)",
            chronology_bce="1,850,000 - 1,770,000 BP",
            source_archives=["Georgian National Museum Archives", "GNAS Paleolithic Reports (Lordkipanidze et al.)"],
            metadata={
                "significance": "Earliest securely dated hominin fossils outside Africa (Homo georgicus, Skulls 1-5)",
                "dating_method": "40Ar/39Ar on Masavera basalt (1.85 Ma) and Matuyama-Olduvai paleomagnetism",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-ORZ-002",
            name_en="Orozmani Lower Paleolithic Site",
            name_ka="ოროზმანი",
            region="Kvemo Kartli (Dmanisi Municipality), Georgia",
            latitude=41.3189,
            longitude=44.1425,
            elevation_m=1180,
            cultural_period="Lower Paleolithic (Oldowan)",
            chronology_bce="1,820,000 - 1,770,000 BP",
            source_archives=["Georgian National Museum Orozmani Expedition (2021-2024)"],
            metadata={
                "significance": "Second Early Pleistocene hominin tooth and Oldowan lithic assemblage in the Mashavera basin",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-DZU-003",
            name_en="Dzudzuana Cave",
            name_ka="ძუძუანას მღვიმე",
            region="Imereti (Chiatura Municipality), Georgia",
            latitude=42.3136,
            longitude=43.3172,
            elevation_m=560,
            cultural_period="Upper Paleolithic",
            chronology_bce="32,000 - 11,000 cal BCE",
            radiocarbon_samples=[
                _c14("RTD-5028", 27400, 300, "Bone collagen (Capra caucasica)", "Unit C (Upper Paleolithic)"),
                _c14("RTT-3821", 23200, 240, "Charcoal", "Unit D"),
            ],
            source_archives=["Georgian National Museum", "Bar-Yosef, Belfer-Cohen & Meshveliani Cave Reports"],
            metadata={
                "significance": "Oldest known spun and dyed wild flax fibers (~34,000 cal BP) and ancient Caucasian paleogenomes",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-ORT-004",
            name_en="Ortvale Klde Rockshelter",
            name_ka="ორთვალა კლდე",
            region="Imereti (Chiatura Municipality), Georgia",
            latitude=42.3019,
            longitude=43.2856,
            elevation_m=530,
            cultural_period="Middle to Upper Paleolithic Transition",
            chronology_bce="43,000 - 26,000 cal BCE",
            radiocarbon_samples=[
                _c14("AA-45862", 34300, 650, "Charcoal", "Layer 4c (Early Upper Paleolithic)"),
                _c14("OxA-11420", 31800, 400, "Bone collagen", "Layer 4b"),
            ],
            source_archives=["N. Tushabramishvili & D.S. Adler Stratigraphic Reports"],
            metadata={
                "significance": "Benchmark stratigraphic sequence for the Neanderthal to Homo sapiens transition in the South Caucasus",
            },
        ),
        # --- NEOLITHIC (SHULAVERI-SHOMU CULTURE) ---
        ArchaeologicalSiteRecord(
            site_id="GEO-GAD-005",
            name_en="Gadachrili Gora",
            name_ka="გადაჭრილი გორა",
            region="Kvemo Kartli (Marneuli Municipality), Georgia",
            latitude=41.4831,
            longitude=44.8194,
            elevation_m=365,
            cultural_period="Early Neolithic (Shulaveri-Shomu Culture)",
            chronology_bce="5980 - 5750 cal BCE",
            radiocarbon_samples=[
                _c14("RTD-7814", 7065, 35, "Charred Triticum grain", "Horizon I, Circular Mudbrick Structure"),
                _c14("UGAMS-25902", 6980, 30, "Charcoal", "Horizon II, Wine Jar Context"),
            ],
            source_archives=["Georgian National Museum Archives", "PNAS 2017 Tartaric Acid Residue Catalog (McGovern et al.)"],
            metadata={
                "significance": "Earliest biomolecular evidence of Vitis vinifera viniculture and Neolithic wine jars (~6000 BCE)",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-SHU-006",
            name_en="Shulaveris Gora",
            name_ka="შულავერის გორა",
            region="Kvemo Kartli (Marneuli Municipality), Georgia",
            latitude=41.4789,
            longitude=44.8236,
            elevation_m=370,
            cultural_period="Early Neolithic (Shulaveri-Shomu Type-Site)",
            chronology_bce="6000 - 5500 cal BCE",
            radiocarbon_samples=[
                _c14("LE-1099", 6920, 90, "Charcoal", "Lower Horizon VIII"),
                _c14("Tb-78", 6655, 85, "Charcoal", "Middle Horizon V"),
            ],
            source_archives=["O. Japaridze & A. Javakhishvili Kvemo Kartli Expedition Reports (1965-1971)"],
            metadata={
                "significance": "Eponymous tell settlement of the Shulaveri-Shomu Neolithic complex with circular mudbrick architecture and obsidian blades",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-KDG-007",
            name_en="Khramis Didi-Gora",
            name_ka="ხრამის დიდი გორა",
            region="Kvemo Kartli, Georgia",
            latitude=41.3911,
            longitude=44.9122,
            elevation_m=320,
            cultural_period="Early Neolithic (Shulaveri-Shomu Culture)",
            chronology_bce="5850 - 5400 cal BCE",
            radiocarbon_samples=[
                _c14("Tb-312", 6850, 70, "Charcoal", "Stratum III"),
                _c14("LE-1340", 6540, 80, "Charred cereal grain", "Stratum II"),
            ],
            source_archives=["Georgian State Museum Kvemo Kartli Monograph Series"],
            metadata={
                "significance": "Large Neolithic tell yielding anthropomorphic clay figurines and tartaric acid wine residues",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-ARU-008",
            name_en="Arukhlo I Tell",
            name_ka="არუხლოს გორა",
            region="Kvemo Kartli (Bolnisi Municipality), Georgia",
            latitude=41.4561,
            longitude=44.6714,
            elevation_m=420,
            cultural_period="Early Neolithic (Shulaveri-Shomu Culture)",
            chronology_bce="5800 - 5350 cal BCE",
            radiocarbon_samples=[
                _c14("Hd-26410", 6790, 45, "Charred Hordeum vulgare", "Concentric Ditch Phase II"),
                _c14("Tb-294", 6610, 75, "Charcoal", "Building Complex IV"),
            ],
            source_archives=["T. Chubinishvili Archives", "DAI Eurasia Department & GNM Joint Reports (Hansen et al.)"],
            metadata={
                "significance": "Neolithic settlement encircled by monumental concentric ditches and Transcaucasian obsidian workshops",
            },
        ),
        # --- CHALCOLITHIC & EARLY BRONZE AGE (KURA-ARAXES) ---
        ArchaeologicalSiteRecord(
            site_id="GEO-SAK-009",
            name_en="Sakdrisi-Kachagiani Prehistoric Gold Mine",
            name_ka="საყდრისი-ყაჩაღიანი",
            region="Kvemo Kartli (Bolnisi/Dmanisi border), Georgia",
            latitude=41.4367,
            longitude=44.4178,
            elevation_m=860,
            cultural_period="Early Bronze Age (Kura-Araxes Culture)",
            chronology_bce="3350 - 2900 cal BCE",
            radiocarbon_samples=[
                _c14("Hd-24811", 4450, 40, "Charcoal from fire-setting mining gallery", "Mine 1/2 Underground Shaft"),
                _c14("MAMS-11420", 4390, 30, "Quercus charcoal", "Gallery B Ore-Crushing Floor"),
            ],
            source_archives=["Georgian-German Mining Archaeology Reports (Stöllner & Gambashidze)", "GNM Metallurgy Collection"],
            metadata={
                "significance": "Earliest known underground hard-rock gold mining complex using fire-setting and stone pounding tools",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-KVA-010",
            name_en="Kvatskhelebi Settlement",
            name_ka="ქვაცხელები",
            region="Shida Kartli (Kareli Municipality), Georgia",
            latitude=42.0258,
            longitude=44.0322,
            elevation_m=635,
            cultural_period="Early Bronze Age (Kura-Araxes Culture)",
            chronology_bce="3100 - 2700 cal BCE",
            radiocarbon_samples=[
                _c14("LE-157", 4310, 80, "Charred wood beam", "Level C1 Burned House"),
                _c14("Tb-29", 4220, 75, "Charred wheat grain", "Level B2"),
            ],
            source_archives=["A. Javakhishvili & L. Glonti Urbnisi-Kvatskhelebi Reports (1962)"],
            metadata={
                "significance": "Exceptionally preserved burned Kura-Araxes village with intact ritual hearths and red-black burnished ware",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-BER-011",
            name_en="Berikldeebi Sanctuary & Settlement",
            name_ka="ბერიკლდეები",
            region="Shida Kartli (Kareli Municipality), Georgia",
            latitude=42.0431,
            longitude=43.9389,
            elevation_m=650,
            cultural_period="Late Chalcolithic to Middle Bronze Age",
            chronology_bce="3800 - 2000 cal BCE",
            radiocarbon_samples=[
                _c14("GIN-6120", 4890, 60, "Charcoal", "Stratum V (Late Chalcolithic)"),
                _c14("Tb-418", 4180, 65, "Charcoal", "Stratum IV (Kura-Araxes)"),
            ],
            source_archives=["A. Javakhishvili Berikldeebi Excavation Archives"],
            metadata={
                "significance": "Stratified cult center at the confluence of the Kura and Prone rivers bridging Chalcolithic, Kura-Araxes, and Bedeni horizons",
            },
        ),
        # --- MIDDLE BRONZE AGE (BEDENI & TRIALETI KURGAN CULTURES) ---
        ArchaeologicalSiteRecord(
            site_id="GEO-BED-012",
            name_en="Bedeni Plateau Kurgan Necropolis",
            name_ka="ბედენის ყურგანები",
            region="Kvemo Kartli (Tetritskaro Municipality), Georgia",
            latitude=41.5514,
            longitude=44.4158,
            elevation_m=1450,
            cultural_period="Early Kurgan Period (Bedeni Culture)",
            chronology_bce="2500 - 2200 cal BCE",
            radiocarbon_samples=[
                _c14("Tb-245", 3920, 65, "Oak burial wagon timber", "Bedeni Kurgan 5"),
                _c14("Hd-19402", 3880, 35, "Chestnut wood", "Bedeni Kurgan 10"),
            ],
            source_archives=["G. Gobedjishvili Bedeni Monograph (1980)", "Georgian National Museum"],
            metadata={
                "significance": "Monumental timber-chambered kurgans containing four-wheeled wooden wagons, textiles, and early arsenical bronzes",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-ANA-013",
            name_en="Ananauri Big Kurgan No. 3",
            name_ka="ანანაურის დიდი ყურგანი №3",
            region="Kakheti (Lagodekhi Municipality), Georgia",
            latitude=41.8022,
            longitude=46.2144,
            elevation_m=480,
            cultural_period="Early Kurgan Period (Bedeni Horizon)",
            chronology_bce="2450 - 2250 cal BCE",
            radiocarbon_samples=[
                _c14("MAMS-18912", 3915, 25, "Oak wagon plank", "Main Burial Chamber"),
                _c14("UGAMS-14205", 3890, 30, "Charred hazelnut shell", "Offering Floor"),
            ],
            source_archives=["Z. Makharadze & GNM Kakheti Kurgan Expedition Reports (2012-2016)"],
            metadata={
                "significance": "Unlooted monumental kurgan yielding two four-wheeled wooden wagons, amber beads, and gold jewelry",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-TRI-014",
            name_en="Trialeti Barrow Cluster (Tsalka Plateau)",
            name_ka="თრიალეთის ყურგანები",
            region="Kvemo Kartli (Tsalka Municipality), Georgia",
            latitude=41.5983,
            longitude=44.0891,
            elevation_m=1540,
            cultural_period="Middle Bronze Age (Trialeti-Vanadzor Culture)",
            chronology_bce="2100 - 1500 cal BCE",
            radiocarbon_samples=[
                _c14("Tb-401", 3580, 60, "Charred pine timber", "Kurgan XVII Processional Causeway"),
                _c14("GrA-48210", 3490, 35, "Bone collagen", "Trialeti Kurgan XV"),
            ],
            source_archives=["B.A. Kuftin Field Archives (1936-1941)", "Georgian National Museum Treasury"],
            metadata={
                "significance": "Elite kurgans with stone causeways and world-renowned silver and gold repoussé goblets",
            },
        ),
        # --- LATE BRONZE / EARLY IRON AGE & COLCHIAN / IBERIAN ANTIQUITY ---
        ArchaeologicalSiteRecord(
            site_id="GEO-GRA-015",
            name_en="Grakliani Hill Sanctuary & Settlement",
            name_ka="გრაკლიანი გორა",
            region="Shida Kartli (Kaspi Municipality), Georgia",
            latitude=41.9764,
            longitude=44.3089,
            elevation_m=590,
            cultural_period="Late Bronze / Early Iron Age to Hellenistic",
            chronology_bce="1100 - 300 cal BCE",
            radiocarbon_samples=[
                _c14("Beta-418920", 2840, 30, "Charred wheat seeds on Temple Altar", "Temple of Fertility Pedestal (10th-11th c. BCE)"),
            ],
            inscriptions=[
                enrich_inscription(
                    inscription_id="EPI-GRA-001",
                    site_id="GEO-GRA-015",
                    script="Grakliani Linear Script (Undeciphered)",
                    language="Unknown Pre-Classical Caucasian/Anatolian",
                    original_text="[Pedestal A & B incised signs on clay altar]",
                    translation_en="Undeciphered cultic dedication on clay altar pedestal",
                    dating_str="10th-8th century BCE (AMS 14C dated)",
                    reference="V. Licheli, Tbilisi State University Grakliani Expedition (2015-2016)",
                )
            ],
            source_archives=["Tbilisi State University Institute of Archaeology (V. Licheli Reports)"],
            metadata={
                "significance": "Multi-layered sanctuary featuring a unique Early Iron Age autochthonous script on a temple altar pedestal",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-VAN-016",
            name_en="Vani Sanctuary & City Site",
            name_ka="ვანის ნაქალაქარი",
            region="Imereti (Vani Municipality), Georgia",
            latitude=42.0856,
            longitude=42.5028,
            elevation_m=185,
            cultural_period="Late Bronze / Classical Colchian & Hellenistic",
            chronology_bce="800 - 50 BCE",
            radiocarbon_samples=[
                _c14("Tb-512", 2420, 50, "Charcoal from sacrificial pit", "5th c. BCE Colchian Rich Burial"),
            ],
            inscriptions=[
                enrich_inscription(
                    inscription_id="EPI-VAN-001",
                    site_id="GEO-VAN-016",
                    script="Ancient Greek",
                    language="Ancient Greek (Hellenistic Koine)",
                    original_text="ΒΑΣΙΛΕΩΣ ΜΙΘΡΑΔΑΤΟΥ ...",
                    translation_en="Fragmentary bronze plaque Greek civic decree from the Vani sanctuary precinct",
                    dating_str="2nd-1st century BCE",
                    reference="T. Kaukhchishvili & O. Lordkipanidze Vani Epigraphic Corpus",
                )
            ],
            source_archives=["O. Lordkipanidze Vani Expedition Archives", "D. Kacharava GNM Reports"],
            metadata={
                "significance": "Major religious and metallurgical center of ancient Colchis with rich granulation goldwork and bronze foundry",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-UPL-017",
            name_en="Uplistsikhe Rock-Hewn City",
            name_ka="უფლისციხე",
            region="Shida Kartli (Gori Municipality), Georgia",
            latitude=41.9672,
            longitude=44.2075,
            elevation_m=580,
            cultural_period="Early Iron Age to Late Antique Iberia",
            chronology_bce="1000 BCE - 500 CE",
            source_archives=["D. Khakhutaishvili Uplistsikhe Monographs", "Georgian National Museum"],
            metadata={
                "significance": "Rock-cut cultic and urban center of ancient Kartli (Iberia) overlooking the Kura River",
            },
        ),
        # --- CLASSICAL IBERIA & EARLY GEORGIAN EPIGRAPHY ---
        ArchaeologicalSiteRecord(
            site_id="GEO-ARM-018",
            name_en="Armazi Citadel (Bagineti) & Necropolis",
            name_ka="არმაზციხე (ბაგინეთი)",
            region="Mtskheta-Mtianeti, Georgia",
            latitude=41.8364,
            longitude=44.7219,
            elevation_m=540,
            cultural_period="Hellenistic / Early Iberian & Late Antique",
            chronology_bce="300 BCE - 400 CE",
            inscriptions=[
                enrich_inscription(
                    inscription_id="EPI-ARM-001",
                    site_id="GEO-ARM-018",
                    script="Ancient Greek & Armazic Aramaic (Bilingual)",
                    language="Ancient Greek / Armazic Aramaic",
                    original_text="ΣΗΡΑΦΕΙΤΙΣ ΖΕΥΑΧΟΥ ΤΟΥ ΝΕΩΤΕΡΟΥ ΠΙΤΙΑΞΟΥ ΘΥΓΑΤΗΡ",
                    translation_en="Serapitis, daughter of Zevakh the Younger, Pitiakhsh, wife of Iodmangan the victorious master of the court of King Xepharnug of Iberia",
                    dating_str="c. 150 CE",
                    reference="G. Tsereteli (1941), The Armazi Bilingual Inscription, Tbilisi",
                )
            ],
            source_archives=["Mtskheta Archaeological Institute Reports", "G. Tsereteli Epigraphic Archive"],
            metadata={
                "significance": "Royal acropolis of Iberia and discovery locus of the Armazi Bilingual (key to deciphering the Armazic script)",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-BOL-019",
            name_en="Bolnisi Sioni Basilica (Epigraphic Locus)",
            name_ka="ბოლნისის სიონი",
            region="Kvemo Kartli (Bolnisi Municipality), Georgia",
            latitude=41.3889,
            longitude=44.5128,
            elevation_m=560,
            cultural_period="Late Antique / Early Christian Kartli",
            chronology_bce="478 - 493 CE",
            inscriptions=[
                enrich_inscription(
                    inscription_id="EPI-BOL-001",
                    site_id="GEO-BOL-019",
                    script="Asomtavruli",
                    language="Old Georgian",
                    original_text="ႵႤ ႣႠႧႳႬႠ ႤႮႨႱႩႭႮႭႱႱႠ ႩႰႤႡႳႪႨႧႳႰႧ ႠႫႨႱ ႤႩႪႤႱႨႨႱႠႷ",
                    translation_en="Christ, have mercy on Bishop David and those who built this church for Your worship",
                    dating_str="493-494 CE (20th year of King Peroz)",
                    reference="Corpus Inscriptionum Georgicarum Vol. I (N. Shoshiashvili, 1980, No. 6-8)",
                )
            ],
            source_archives=["Corpus Inscriptionum Georgicarum (Lapidary Inscriptions, Vol. I)", "K. Kekelidze Institute of Manuscripts"],
            metadata={
                "significance": "Oldest securely dated surviving Old Georgian Asomtavruli stone inscriptions in Georgia (late 5th century CE)",
            },
        ),
        ArchaeologicalSiteRecord(
            site_id="GEO-JVR-020",
            name_en="Mtskheta Jvari Monastery Reliefs",
            name_ka="მცხეთის ჯვრის მონასტერი",
            region="Mtskheta-Mtianeti, Georgia",
            latitude=41.8383,
            longitude=44.7333,
            elevation_m=655,
            cultural_period="Early Medieval Kartli (Erismtavari Period)",
            chronology_bce="586 - 605 CE",
            inscriptions=[
                enrich_inscription(
                    inscription_id="EPI-JVR-001",
                    site_id="GEO-JVR-020",
                    script="Asomtavruli",
                    language="Old Georgian",
                    original_text="ႼႫႨႣႠႭ ႫႨႵႠႤႪ ႫႧႠႥႠႰႠႬႢႤႪႭႦႭ ႣႤႫႤႲႰႤႱ ႳႮႠႲႭႱႱႠ ႫႤႭႾ ႤႷႠႥ",
                    translation_en="Saint Michael Archangel, intercede for Demetre the Hypatos",
                    dating_str="586-605 CE",
                    reference="Corpus Inscriptionum Georgicarum Vol. I (N. Shoshiashvili, 1980, No. 13)",
                )
            ],
            source_archives=["Corpus Inscriptionum Georgicarum", "G. Chubinashvili History of Georgian Architecture"],
            metadata={
                "significance": "Monumental facade reliefs with benchmark Asomtavruli inscriptions naming Stephanos Patricius and Demetre Hypatos",
            },
        ),
    ]
