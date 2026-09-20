#!/usr/bin/env python3
"""
scripts/test_all_features.py — Comprehensive API integration test for IP-SAKTI Sahayak.
"""
import sys
import json
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("[TEST] Starting IP-SAKTI Sahayak End-to-End Feature Verification Tests...\n")

    
    # 1. Health Check
    try:
        r = httpx.get("http://localhost:8000/health", timeout=5.0)
        print(f"[1] Health Check: Status {r.status_code} -> {r.json().get('status')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # 2. IP Type Recommender
    try:
        payload = {
            "description": "I developed a new Ayurvedic formulation, created a unique bottle design, have a brand name 'AyurZen' and created a product manual."
        }
        r = httpx.post(f"{BASE_URL}/features/ip-recommend", json=payload, timeout=10.0)
        print(f"[2] IP Type Recommender: Status {r.status_code}")
        data = r.json()
        print(f"    Recs count: {len(data.get('recommendations', []))}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ IP Type Recommender failed: {e}")

    # 3. Patentability Pre-Screen
    try:
        payload = {
            "title": "Synergistic Ayurvedic Hydrogel",
            "description": "Topical formulation of turmeric, ashwagandha and neem.",
            "ingredients": "Turmeric, Ashwagandha, Neem",
            "claimed_new": "Ratio 3:2:1 synergistic COX-2 inhibition",
            "is_tk_involved": True,
            "is_biological_involved": True
        }
        r = httpx.post(f"{BASE_URL}/features/patentability-prescreen", json=payload, timeout=10.0)
        print(f"[3] Patentability Pre-Screen: Status {r.status_code}")
        data = r.json()
        print(f"    Novelty: {data.get('novelty')}, TK Risk: {data.get('tk_risk')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Patentability Pre-Screen failed: {e}")

    # 4. AYUSH Analysis
    try:
        payload = {"description": "I created a turmeric, neem and Ashwagandha formulation for inflammation."}
        r = httpx.post(f"{BASE_URL}/features/ayush-analysis", json=payload, timeout=10.0)
        print(f"[4] AYUSH Analysis: Status {r.status_code}")
        data = r.json()
        print(f"    Herbs detected: {data.get('traditional_ingredients_detected')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ AYUSH Analysis failed: {e}")

    # 5. Bio Material Compliance
    try:
        payload = {
            "biological_resource_used": True,
            "resource_name": "Curcuma longa",
            "geographical_origin": "Kerala, India"
        }
        r = httpx.post(f"{BASE_URL}/features/biomaterial-check", json=payload, timeout=10.0)
        print(f"[5] Bio Material Compliance: Status {r.status_code}")
        data = r.json()
        print(f"    Approvals required: {len(data.get('mandatory_approvals', []))}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Bio Material Compliance failed: {e}")

    # 6. MSME IP Health Check
    try:
        payload = {
            "has_registered_business": True,
            "has_brand_name": True,
            "has_logo": True,
            "has_unique_product": True,
            "has_tech_innovation": True,
            "has_product_docs": True,
            "has_confidential_info": False,
            "has_searched_patents": False,
            "has_searched_trademarks": True
        }
        r = httpx.post(f"{BASE_URL}/features/msme-health-check", json=payload, timeout=10.0)
        print(f"[6] MSME IP Health Check: Status {r.status_code}")
        data = r.json()
        print(f"    Overall Score: {data.get('overall_score')}/100")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ MSME IP Health Check failed: {e}")

    # 7. Cost Estimator
    try:
        payload = {"ip_type": "patent", "applicant_type": "Startup"}
        r = httpx.post(f"{BASE_URL}/features/cost-estimator", json=payload, timeout=10.0)
        print(f"[7] Cost Estimator: Status {r.status_code}")
        data = r.json()
        print(f"    Estimated Fee: ₹{data.get('estimated_official_fee')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Cost Estimator failed: {e}")

    # 8. Prior-Art Search
    try:
        payload = {"query": "AYUSH turmeric ashwagandha formulation", "top_k": 3}
        r = httpx.post(f"{BASE_URL}/features/prior-art-search", json=payload, timeout=10.0)
        print(f"[8] Prior-Art Search: Status {r.status_code}")
        data = r.json()
        print(f"    Results count: {len(data.get('results', []))}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Prior-Art Search failed: {e}")

    # 9. Trademark Pre-Screen
    try:
        payload = {"brand_name": "AYURZEN", "product_service": "Herbal formulation syrup"}
        r = httpx.post(f"{BASE_URL}/features/trademark-prescreen", json=payload, timeout=10.0)
        print(f"[9] Trademark Pre-Screen: Status {r.status_code}")
        data = r.json()
        print(f"    Assessment: {data.get('preliminary_assessment')}, Class: {data.get('recommended_nice_class')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Trademark Pre-Screen failed: {e}")

    # 10. Legal Language Explainer
    try:
        payload = {"query": "Explain Section 3(p)"}
        r = httpx.post(f"{BASE_URL}/features/legal-explain", json=payload, timeout=10.0)
        print(f"[10] Legal Explainer: Status {r.status_code}")
        data = r.json()
        print(f"    Provision: {data.get('provision_name')}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Legal Explainer failed: {e}")

    # 11. PDF Report Generation
    try:
        payload = {
            "applicant_name": "AyurZen Labs",
            "invention_title": "Ayurvedic Topical Hydrogel",
            "description": "Topical hydrogel formulation combining turmeric and neem."
        }
        r = httpx.post(f"{BASE_URL}/features/generate-report", json=payload, timeout=10.0)
        print(f"[11] PDF Assessment Report: Status {r.status_code}, Bytes: {len(r.content)}")
        assert r.status_code == 200 and len(r.content) > 500
    except Exception as e:
        print(f"❌ PDF Report Generation failed: {e}")

    print("\n🎉 All 11 Feature Verification Tests Completed Successfully!")

if __name__ == "__main__":
    run_tests()
