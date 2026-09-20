"""
Mock IP-SAKTI RAG Engine.
Simulates the core retrieval-augmented generation backend for Indian Patent,
Trademark, and Copyright knowledge to demonstrate full end-to-end integration.
"""

from typing import Dict, Any


class MockIPRAGEngine:
    """Simulates the IP-SAKTI RAG retrieval engine over Indian IP laws."""

    KNOWLEDGE_BASE = {
        "ayurvedic": (
            "Under the Indian Patents Act, 1970, patenting an Ayurvedic or herbal formulation requires satisfying key statutory conditions:\n"
            "1. **Section 3(p) Compliance**: An invention which, in effect, is traditional knowledge or an aggregation of known properties of traditionally known components is NOT patentable.\n"
            "2. **Novelty & Synergism**: You must demonstrate that your formulation produces a surprising, synergistic therapeutic effect that goes beyond the additive effects of the individual herbs.\n"
            "3. **National Biodiversity Authority (NBA) Approval**: Under Section 6 of the Biological Diversity Act, 2002, if you use biological resources from India, you must obtain prior permission from the NBA before patent grant.\n"
            "4. **Filing Steps**: File Form 1 (Application for Grant of Patent) and Form 2 (Provisional or Complete Specification) along with Form 3 and Form 5 at the Indian Patent Office (IPO)."
        ),
        "software": (
            "In India, software and computer programs per se are governed by Section 3(k) of the Patents Act, 1970 and the CRI (Computer Related Inventions) Guidelines:\n"
            "1. Pure software code, algorithms, and mathematical methods are not patentable per se.\n"
            "2. Software is patentable if it demonstrates a technical effect, solves a technical problem, or operates in combination with novel hardware.\n"
            "3. Software source code and algorithms can also be protected under the Copyright Act, 1957."
        ),
        "trademark": (
            "To register a brand name, logo, or slogan under the Trade Marks Act, 1999:\n"
            "1. **Prior Art & Conflict Search**: Perform a public search on the IP India portal across the relevant Nice Classification (Classes 1-45).\n"
            "2. **Form TM-A**: Submit Form TM-A online on the IP India e-filing portal.\n"
            "3. **Government Fees**: ₹4,500 for Individuals, Startups, and MSMEs (50% fee concession), ₹9,000 for other entities.\n"
            "4. **Examination & Journal Publication**: After examination, the mark is published in the Trade Marks Journal for 4 months for opposition before certificate issuance."
        ),
        "provisional": (
            "A Provisional Patent Specification in India provides immediate priority protection:\n"
            "1. **Priority Date**: Secures the earliest filing date before disclosing the invention publicly.\n"
            "2. **12 Months Deadline**: You must file the Complete Specification within 12 months (non-extendable) from the provisional filing date.\n"
            "3. **Key Forms**: Form 1 (Application), Form 2 (Provisional Specification detailing the invention title and description), Form 3 (Statement of foreign undertakings)."
        ),
        "fees": (
            "Official Fee Structure under the Indian Patent Rules:\n"
            "- **Natural Person / Startup / MSME**: Form 1 (Filing) = ₹1,600 (online). Form 18 (Request for Examination) = ₹4,000.\n"
            "- **Large Entities / Others**: Form 1 = ₹8,000. Form 18 = ₹20,000.\n"
            "- Startups and MSMEs receive up to an 80% rebate on patent filing and examination fees."
        )
    }

    def query(self, normalized_english_query: str, intent_category: str = "general_inquiry") -> Dict[str, Any]:
        """
        Retrieves relevant legal IP context and returns an English answer.
        """
        q_lower = normalized_english_query.lower()

        # Keyword based retrieval over knowledge base
        if "ayurvedic" in q_lower or "traditional knowledge" in q_lower or "medicine" in q_lower:
            answer = self.KNOWLEDGE_BASE["ayurvedic"]
            topic = "Ayurvedic Formulation Patenting & Section 3(p)"
        elif "software" in q_lower or "algorithm" in q_lower or "app" in q_lower:
            answer = self.KNOWLEDGE_BASE["software"]
            topic = "Software Patentability & Section 3(k)"
        elif "trademark" in q_lower or "logo" in q_lower or "brand" in q_lower:
            answer = self.KNOWLEDGE_BASE["trademark"]
            topic = "Trademark Registration Process & Form TM-A"
        elif "provisional" in q_lower:
            answer = self.KNOWLEDGE_BASE["provisional"]
            topic = "Provisional Patent Specification Filing"
        elif "fees" in q_lower or "cost" in q_lower or "rebate" in q_lower:
            answer = self.KNOWLEDGE_BASE["fees"]
            topic = "Patent & IP Fee Structure (Startup/MSME Subsidies)"
        else:
            answer = (
                f"Regarding your query on '{normalized_english_query}':\n"
                "Under the Indian Patents Act, 1970, an invention must satisfy three core criteria: "
                "Novelty (new worldwide), Inventive Step (non-obvious to a person skilled in the art), and "
                "Industrial Applicability. Please consult Form 1 & 2 on ipindia.gov.in."
            )
            topic = "General Indian Patent Provisions"

        return {
            "query": normalized_english_query,
            "answer": answer,
            "topic": topic,
            "sources": ["Indian Patents Act, 1970", "IPO Manual of Patent Office Practice & Procedure", "ipindia.gov.in"]
        }
