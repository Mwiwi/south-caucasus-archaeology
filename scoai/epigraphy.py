"""
Epigraphic script conversion and transliteration module for South Caucasus inscriptions.
Supports ancient Georgian Asomtavruli (Mrglovani, U+10A0..U+10C5),
Nuskhuri (Khutsuri, U+2D00..U+2D25), modern Mkhedruli (U+10D0..U+10F5),
and scholarly Caucasian linguistic Latin transliteration.
"""

from typing import Dict
from scoai.schema import EpigraphicInscription


ASOMTAVRULI_START = 0x10A0
ASOMTAVRULI_END = 0x10C5
MKHEDRULI_START = 0x10D0
MKHEDRULI_END = 0x10F5
NUSKHURI_START = 0x2D00
NUSKHURI_END = 0x2D25

# Scholarly Kartvelological Latin transliteration (distinguishing aspirated vs. ejective stops)
MKHEDRULI_TO_SCHOLARLY_LATIN: Dict[str, str] = {
    "ა": "a",
    "ბ": "b",
    "გ": "g",
    "დ": "d",
    "ე": "e",
    "ვ": "v",
    "ზ": "z",
    "ჱ": "ē",  # Old Georgian He (ey)
    "თ": "t",
    "ი": "i",
    "კ": "k'",
    "ლ": "l",
    "მ": "m",
    "ნ": "n",
    "ჲ": "y",  # Old Georgian Hie
    "ო": "o",
    "პ": "p'",
    "ჟ": "zh",
    "რ": "r",
    "ს": "s",
    "ტ": "t'",
    "ჳ": "w",  # Old Georgian Vie
    "უ": "u",
    "ფ": "p",
    "ქ": "k",
    "ღ": "gh",
    "ყ": "q'",
    "შ": "sh",
    "ჩ": "ch",
    "ც": "ts",
    "ძ": "dz",
    "წ": "ts'",
    "ჭ": "ch'",
    "ხ": "kh",
    "ჴ": "q",  # Old Georgian Qar (uvular fricative/aspirated stop)
    "ჯ": "j",
    "ჰ": "h",
    "ჵ": "ō",  # Old Georgian Hoe
}


def asomtavruli_to_mkhedruli(text: str) -> str:
    """Converts Old Georgian Asomtavruli (U+10A0..U+10C5) or Nuskhuri (U+2D00..U+2D25) to Mkhedruli."""
    out = []
    for ch in text:
        code = ord(ch)
        if ASOMTAVRULI_START <= code <= ASOMTAVRULI_END:
            out.append(chr(code + (MKHEDRULI_START - ASOMTAVRULI_START)))
        elif NUSKHURI_START <= code <= NUSKHURI_END:
            out.append(chr(code - (NUSKHURI_START - MKHEDRULI_START)))
        else:
            out.append(ch)
    return "".join(out)


def mkhedruli_to_asomtavruli(text: str) -> str:
    """Converts Mkhedruli (U+10D0..U+10F5) or Nuskhuri to Old Georgian Asomtavruli (U+10A0..U+10C5)."""
    out = []
    for ch in text:
        code = ord(ch)
        if MKHEDRULI_START <= code <= MKHEDRULI_END:
            out.append(chr(code - (MKHEDRULI_START - ASOMTAVRULI_START)))
        elif NUSKHURI_START <= code <= NUSKHURI_END:
            out.append(chr(code - (NUSKHURI_START - ASOMTAVRULI_START)))
        else:
            out.append(ch)
    return "".join(out)


def mkhedruli_to_nuskhuri(text: str) -> str:
    """Converts Mkhedruli or Asomtavruli to ecclesiastical Nuskhuri script (U+2D00..U+2D25)."""
    mkh = asomtavruli_to_mkhedruli(text)
    out = []
    for ch in mkh:
        code = ord(ch)
        if MKHEDRULI_START <= code <= MKHEDRULI_END:
            out.append(chr(code + (NUSKHURI_START - MKHEDRULI_START)))
        else:
            out.append(ch)
    return "".join(out)


def transliterate_georgian_to_latin(text: str) -> str:
    """Transliterates Asomtavruli, Nuskhuri, or Mkhedruli text into scholarly Latin notation."""
    mkh = asomtavruli_to_mkhedruli(text)
    return "".join(MKHEDRULI_TO_SCHOLARLY_LATIN.get(ch, ch) for ch in mkh)


def enrich_inscription(
    inscription_id: str,
    site_id: str,
    script: str,
    language: str,
    original_text: str,
    translation_en: str,
    dating_str: str,
    reference: str,
) -> EpigraphicInscription:
    """Builds an EpigraphicInscription and automatically populates Mkhedruli and Latin transliterations."""
    if script in ("Asomtavruli", "Nuskhuri", "Asomtavruli (Mrglovani)"):
        mkh = asomtavruli_to_mkhedruli(original_text)
        lat = transliterate_georgian_to_latin(original_text)
    else:
        mkh = None
        lat = None
    return EpigraphicInscription(
        inscription_id=inscription_id,
        site_id=site_id,
        script=script,
        language=language,
        original_text=original_text,
        mkhedruli_transliteration=mkh,
        latin_transliteration=lat,
        translation_en=translation_en,
        dating_str=dating_str,
        reference=reference,
    )
