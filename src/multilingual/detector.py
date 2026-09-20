"""
Language and Script Detector for IP-SAKTI Sahayak.
Distinguishes between Pure Hindi (Devanagari), Colloquial Hinglish (Roman Script),
Pure English, Tamil, and Tanglish.
"""

import re
from typing import Dict, Any, Tuple

# Common colloquial Hinglish tokens (phonetic markers in Roman script)
HINGLISH_MARKERS = {
    # Pronouns & Question words
    "kya", "kaise", "kab", "kaha", "kahan", "kyu", "kyun", "kaun", "kiska", "kiski",
    "maine", "mera", "meri", "mere", "mujhe", "mujhko", "hum", "humne", "hamara",
    "aap", "aapka", "aapki", "tum", "tumhara", "isko", "isse", "iska", "iski", "unko", "ye", "wo", "yeh", "woh",
    # Verbs & Auxiliaries
    "hai", "hain", "ho", "hoon", "tha", "thi", "the", "hoga", "hogi", "honge",
    "karna", "kare", "karein", "karu", "karun", "kar", "karo", "kiya", "kiye",
    "banayi", "banaya", "banaye", "banani", "chahiye", "chahta", "chahti",
    "milega", "milegi", "milenge", "sakta", "sakti", "sakte", "lagta", "lagega",
    "batao", "bataiye", "samjhao", "dekh", "dekho", "aata", "aati", "hota", "hoti",
    # Prepositions & Connectors
    "me", "mein", "pe", "par", "se", "ko", "aur", "ya", "lekin", "magar", "parantu",
    "nahi", "nahin", "mat", "bhi", "sirf", "kitna", "kitni", "kitne", "wala", "wali",
    "ke", "ki", "ka", "liye", "baad", "pehle", "andar", "bahar", "saath"
}

# Common colloquial Tanglish tokens
TANGLISH_MARKERS = {
    "epdi", "enna", "enga", "yen", "yaaru", "edhu", "ippadi", "appadi",
    "panradhu", "pannalaam", "panna", "pannanum", "irukku", "kedaikkuma",
    "sollunga", "theriyuma", "mudiyuma", "aagum", "evvalavu", "enakku", "unga"
}

# Unicode ranges
DEVANAGARI_RANGE = (0x0900, 0x097F)
TAMIL_RANGE = (0x0B80, 0x0BFF)


def _count_script_chars(text: str) -> Dict[str, int]:
    """Counts character occurrences by script block."""
    counts = {
        "devanagari": 0,
        "tamil": 0,
        "latin": 0,
        "other": 0
    }
    for ch in text:
        cp = ord(ch)
        if DEVANAGARI_RANGE[0] <= cp <= DEVANAGARI_RANGE[1]:
            counts["devanagari"] += 1
        elif TAMIL_RANGE[0] <= cp <= TAMIL_RANGE[1]:
            counts["tamil"] += 1
        elif ('a' <= ch.lower() <= 'z'):
            counts["latin"] += 1
        elif not ch.isspace() and not ch.isdigit() and ch not in ",.?!;:'\"-()[]{}":
            counts["other"] += 1
    return counts


def detect_language_and_script(text: str) -> Dict[str, Any]:
    """
    Detects language and script of the input query.
    
    Returns:
    {
        "language": "hinglish" | "hindi" | "english" | "tanglish" | "tamil",
        "script": "latin" | "devanagari" | "tamil",
        "confidence": float,
        "is_code_mixed": bool,
        "details": dict
    }
    """
    if not text or not text.strip():
        return {
            "language": "english",
            "script": "latin",
            "confidence": 1.0,
            "is_code_mixed": False,
            "details": {"reason": "empty_input"}
        }

    script_counts = _count_script_chars(text)
    total_letters = script_counts["devanagari"] + script_counts["tamil"] + script_counts["latin"]

    # 1. Native Devanagari Script (Pure Hindi / Marathi / Sanskrit)
    if script_counts["devanagari"] > 0 and (script_counts["devanagari"] / max(total_letters, 1)) > 0.4:
        confidence = min(0.99, round(script_counts["devanagari"] / max(total_letters, 1), 2))
        return {
            "language": "hindi",
            "script": "devanagari",
            "confidence": confidence,
            "is_code_mixed": script_counts["latin"] > 0,
            "details": {"script_counts": script_counts}
        }

    # 2. Native Tamil Script
    if script_counts["tamil"] > 0 and (script_counts["tamil"] / max(total_letters, 1)) > 0.4:
        confidence = min(0.99, round(script_counts["tamil"] / max(total_letters, 1), 2))
        return {
            "language": "tamil",
            "script": "tamil",
            "confidence": confidence,
            "is_code_mixed": script_counts["latin"] > 0,
            "details": {"script_counts": script_counts}
        }

    # 3. Latin Script (English vs Hinglish vs Tanglish)
    tokens = re.findall(r'[a-zA-Z]+', text.lower())
    if not tokens:
        return {
            "language": "english",
            "script": "latin",
            "confidence": 0.8,
            "is_code_mixed": False,
            "details": {"reason": "no_alpha_tokens"}
        }

    hinglish_matches = [t for t in tokens if t in HINGLISH_MARKERS]
    tanglish_matches = [t for t in tokens if t in TANGLISH_MARKERS]

    num_tokens = len(tokens)
    hinglish_ratio = len(hinglish_matches) / max(num_tokens, 1)
    tanglish_ratio = len(tanglish_matches) / max(num_tokens, 1)

    # If Tanglish markers dominate
    if len(tanglish_matches) >= 2 or tanglish_ratio >= 0.25:
        return {
            "language": "tanglish",
            "script": "latin",
            "confidence": min(0.95, 0.6 + tanglish_ratio),
            "is_code_mixed": True,
            "details": {
                "matched_markers": tanglish_matches,
                "ratio": round(tanglish_ratio, 2)
            }
        }

    # If Hinglish markers are detected (even 1-2 distinct colloquial words like 'kaise', 'banayi hai', 'chahiye')
    if len(hinglish_matches) >= 1 and (len(hinglish_matches) >= 2 or hinglish_ratio >= 0.15 or any(t in ("kaise", "banayi", "chahiye", "karu", "hoga", "kya", "mera", "maine") for t in hinglish_matches)):
        return {
            "language": "hinglish",
            "script": "latin",
            "confidence": min(0.98, 0.65 + hinglish_ratio * 0.5),
            "is_code_mixed": True,
            "details": {
                "matched_markers": hinglish_matches,
                "ratio": round(hinglish_ratio, 2)
            }
        }

    # Default to Pure English
    return {
        "language": "english",
        "script": "latin",
        "confidence": 0.95,
        "is_code_mixed": False,
        "details": {"matched_markers": hinglish_matches}
    }
