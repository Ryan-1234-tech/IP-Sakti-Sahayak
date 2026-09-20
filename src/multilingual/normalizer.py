"""
Query Normalizer for IP-SAKTI Sahayak.
Normalizes colloquial Hindi, Hinglish, and Tanglish queries into formal English
search queries optimized for RAG retrieval over Indian Patent & IP databases.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
try:
    from src import config
    from src.multilingual.detector import detect_language_and_script
except (ImportError, ModuleNotFoundError):
    import config
    from multilingual.detector import detect_language_and_script

logger = logging.getLogger(__name__)

# IP Domain Keywords and Intent Taxonomy
IP_INTENT_PATTERNS = [
    (r"\b(fees|cost|kharcha|paisa|charges|expenditure|discount|rebate|subsidy|startup|msme)\b", "fee_structure_and_subsidies"),
    (r"\b(ayurvedic|ayurveda|aurbedic|herb|herbal|medicine|dawa|dawai|dwayi|aushadhi|formulation)\b", "patent_ayurvedic_traditional_knowledge"),
    (r"\b(software|algorithm|computer program|source code|ai model|\bapp\b|mobile app|section 3\(k\)|3\(k\))\b", "patent_software_cr_inventions"),
    (r"\b(infringement|chori|nakal|copy kar|violation|legal notice|court)\b", "ip_enforcement_infringement"),
    (r"\b(provisional|temporary|draft|kachhi|form 1|form 2|form 3)\b", "provisional_patent_filing"),
    (r"\b(trademark|trade mark|logo|brand|brand name|symbol|tm-a)\b", "trademark_registration"),
    (r"\b(copyright|copy right|book|music|song|video|script|literary)\b", "copyright_protection"),
    (r"\b(validity|timeline|duration|kitne saal|kitna time|kab tak|expire|renewal)\b", "ip_validity_timeline"),
    (r"\b(prior art|novelty|search|check|pehle se|existing)\b", "prior_art_search_novelty")
]

# Hinglish grammar & phrasing substitution dictionary for rule-based fallback
HINGLISH_PHRASE_MAPPINGS = [
    # Question structures
    (r"\bmaine\b\s+(.*?)\s+\bbanayi hai\b", r"I have developed \1"),
    (r"\bmaine\b\s+(.*?)\s+\bbanaya hai\b", r"I have developed \1"),
    (r"\bmaine\b\s+(.*?)\s+\binvent kiya hai\b", r"I have invented \1"),
    (r"\bisko\s+patent\s+kaise\s+karu\b", "how can I patent it in India"),
    (r"\biska\s+patent\s+kaise\s+(milega|hoga|karein|karwaye)\b", "how to obtain a patent for this in India"),
    (r"\bpatent\s+kaise\s+(karu|kare|karein|karwaye|hoga)\b", "how to apply for a patent in India"),
    (r"\bkaise\s+register\s+(kare|karein|karu|hoga)\b", "how to register"),
    (r"\bkitna\s+fees\s+lagta\s+hai\b", "what are the official government fees"),
    (r"\bkitna\s+kharcha\s+(aayega|lagta hai|hoga)\b", "what is the cost and fee breakdown"),
    (r"\bkitna\s+time\s+lagta\s+hai\b", "how much time does the process take"),
    (r"\bkaun\s+se\s+documents\s+chahiye\b", "what documents are required"),
    (r"\bkya\s+process\s+hai\b", "what is the step by step procedure"),
    (r"\bkya\s+mai\b", "can I"),
    (r"\bkya\s+ye\s+patent\s+ho\s+sakta\s+hai\b", "is this patentable under Indian Patent Act"),
    (r"\bmujhe\s+apne\b", "I want to get my"),
    (r"\bapne\s+brand\s+ka\s+logo\b", "my brand logo"),
    (r"\bchori\s+hone\s+se\s+kaise\s+bachaye\b", "how to protect from infringement"),
]


class QueryNormalizer:
    """Normalizes multilingual queries into canonical English for RAG indexing."""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    def normalize(self, query: str, detected_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main normalization method.
        Cascades: LLM -> Neural Machine Translation -> Rule-based IP Normalizer.
        """
        text = query.strip()
        if not text:
            return {
                "normalized_query": "",
                "intent_category": "general_inquiry",
                "extracted_keywords": [],
                "engine": "empty"
            }

        if detected_info is None:
            detected_info = detect_language_and_script(text)

        lang = detected_info["language"]
        script = detected_info["script"]

        # If already standard English without colloquial Hinglish tokens
        if lang == "english" and not detected_info.get("is_code_mixed", False):
            intent, keywords = self._extract_intent_and_keywords(text)
            return {
                "normalized_query": text,
                "intent_category": intent,
                "extracted_keywords": keywords,
                "engine": "passthrough_english"
            }

        # 1. Try LLM normalization if API key configured
        if self.use_llm and (config.GEMINI_API_KEY or config.OPENAI_API_KEY):
            llm_result = self._normalize_with_llm(text, lang)
            if llm_result:
                return llm_result

        # 2. Devanagari Hindi or Native Tamil -> Neural Translation + Semantic Refinement
        if script in ("devanagari", "tamil"):
            translated_text = self._translate_neural(text, source_lang=lang)
            intent, keywords = self._extract_intent_and_keywords(translated_text + " " + text)
            normalized = self._refine_english_query(translated_text, intent)
            return {
                "normalized_query": normalized,
                "intent_category": intent,
                "extracted_keywords": keywords,
                "engine": "neural_translation_refiner"
            }

        # 3. Hinglish / Tanglish in Latin Script -> Rule-based and Phonetic Normalizer
        normalized, intent, keywords = self._normalize_hinglish_rule_based(text)
        return {
            "normalized_query": normalized,
            "intent_category": intent,
            "extracted_keywords": keywords,
            "engine": "rule_based_hinglish_normalizer"
        }

    def _normalize_with_llm(self, text: str, lang: str) -> Optional[Dict[str, Any]]:
        """Invokes LLM (Gemini / OpenAI) to accurately disambiguate colloquial Hinglish/Hindi."""
        system_prompt = (
            "You are the Multilingual Query Processor for IP-SAKTI Sahayak (Indian Patent & IP Assistant).\n"
            "Convert the user's colloquial Hindi/Hinglish/Tanglish query into a clear, concise, "
            "search-optimized English question suitable for an Indian Patent Act & RAG vector search.\n"
            "Respond strictly with valid JSON with keys: 'normalized_query', 'intent_category', 'extracted_keywords'."
        )
        user_prompt = f"User Query ({lang}): \"{text}\""

        # Gemini
        if config.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                model = genai.GenerativeModel(
                    model_name=config.GEMINI_MODEL,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
                data = json.loads(response.text)
                data["engine"] = "gemini_llm"
                return data
            except Exception as e:
                logger.warning(f"Gemini normalization failed: {e}")

        # OpenAI
        if config.OPENAI_API_KEY:
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": config.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=8)
                if resp.status_code == 200:
                    data = json.loads(resp.json()["choices"][0]["message"]["content"])
                    data["engine"] = "openai_llm"
                    return data
            except Exception as e:
                logger.warning(f"OpenAI normalization failed: {e}")

        return None

    def _translate_neural(self, text: str, source_lang: str) -> str:
        """Translates native script text to English via deep-translator."""
        try:
            from deep_translator import GoogleTranslator
            src = "hi" if source_lang in ("hindi", "hi") else ("ta" if source_lang in ("tamil", "ta") else "auto")
            return GoogleTranslator(source=src, target="en").translate(text)
        except Exception as e:
            logger.warning(f"Neural translation error: {e}")
            return text

    def _normalize_hinglish_rule_based(self, text: str) -> Tuple[str, str, List[str]]:
        """Rule-based, offline normalizer for colloquial Hinglish."""
        lower = text.lower()
        normalized = lower

        # Apply specific phrasing substitutions
        for pattern, replacement in HINGLISH_PHRASE_MAPPINGS:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        # Detect intent and keywords
        intent, keywords = self._extract_intent_and_keywords(text)

        # Standardize query format
        if "ayurvedic" in lower or "ayurveda" in lower:
            normalized = "How can I patent my Ayurvedic medicine formulation in India?"
        elif "infringement" in intent or "copy" in lower or "chori" in lower:
            normalized = "What legal actions can I take against brand or patent infringement in India?"
        elif "fee" in intent or "discount" in lower or "rebate" in lower:
            normalized = "What are the official government fees and startup discounts for patent or trademark filing in India?"
        elif "validity" in intent or "kitne saal" in lower:
            normalized = "What is the statutory validity period of a granted patent in India?"
        elif "provisional" in lower:
            normalized = "What is the procedure and timeline for filing a provisional patent specification in India?"
        elif "software" in lower or "algorithm" in lower or "mobile app" in lower:
            normalized = "How to patent software or mobile application algorithms under Indian Patent Office guidelines (CRI)?"
        elif "trademark" in lower or "brand" in lower or "logo" in lower:
            normalized = "How can I register my brand name and logo as a trademark in India?"
        elif "document" in lower or "documents" in lower or "thevai" in lower:
            normalized = "What documents and forms are required to apply for a patent in India?"
        else:
            # Fallback: clean extra punctuation and capitalize
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            if not normalized.endswith("?"):
                normalized += "?"
            normalized = normalized[0].upper() + normalized[1:]

        return normalized, intent, keywords

    def _refine_english_query(self, raw_english: str, intent: str) -> str:
        """Refines translated English into a clear patent query."""
        raw_english = raw_english.strip()
        if not raw_english.endswith("?"):
            raw_english += "?"
        return raw_english[0].upper() + raw_english[1:]

    def _extract_intent_and_keywords(self, text: str) -> Tuple[str, List[str]]:
        """Extracts primary IP intent and domain keywords."""
        lower = text.lower()
        intent = "general_patent_inquiry"

        for pattern, cat in IP_INTENT_PATTERNS:
            if re.search(pattern, lower):
                intent = cat
                break

        # Extract keywords
        extracted = []
        ip_terms = [
            "ayurvedic medicine", "ayurveda", "patent", "trademark", "copyright",
            "provisional specification", "complete specification", "form 1", "form 2",
            "fees", "cost", "infringement", "prior art", "software", "novelty",
            "traditional knowledge", "section 3(d)", "section 3(p)", "nba approval"
        ]
        for term in ip_terms:
            if term in lower:
                extracted.append(term)

        # Fallback keyword extraction if empty
        if not extracted:
            tokens = [w for w in re.findall(r'\w+', lower) if len(w) > 3]
            extracted = tokens[:4]

        return intent, extracted
