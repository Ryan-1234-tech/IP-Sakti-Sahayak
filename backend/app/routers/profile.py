"""
routers/profile.py — CRUD endpoints for BusinessProfile & computed Compliance Passport.

Endpoints:
  - POST /api/profile          : Create a BusinessProfile
  - GET  /api/profile          : List profiles / get latest
  - GET  /api/profile/{id}     : Get profile by ID
  - PUT  /api/profile/{id}     : Update profile by ID
  - GET  /api/profile/{id}/passport : Computed IP Compliance Passport
"""
import json
import logging
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db import BusinessProfile
from app.models.schemas import (
    AssetBreakdown,
    BusinessProfileCreate,
    BusinessProfileResponse,
    BusinessProfileUpdate,
    ChecklistItem,
    CompliancePassportResponse,
    IPAssetSchema,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _to_response(profile: BusinessProfile) -> BusinessProfileResponse:
    """Helper to convert ORM model to Pydantic response."""
    try:
        assets_raw = json.loads(profile.ip_assets_json or "[]")
        ip_assets = [IPAssetSchema(**a) for a in assets_raw]
    except Exception:
        ip_assets = []

    return BusinessProfileResponse(
        id=profile.id,
        company_name=profile.company_name,
        sector=profile.sector,
        company_type=profile.company_type,
        registration_number=profile.registration_number,
        state=profile.state,
        ip_assets=ip_assets,
        created_at=profile.created_at.isoformat() if profile.created_at else datetime.utcnow().isoformat(),
        updated_at=profile.updated_at.isoformat() if profile.updated_at else datetime.utcnow().isoformat(),
    )


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------


@router.post("/profile", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED, summary="Create Business Profile")
async def create_profile(payload: BusinessProfileCreate, db: AsyncSession = Depends(get_db)) -> BusinessProfileResponse:
    """Create a new company business profile with IP assets."""
    profile_id = str(uuid.uuid4())
    assets_json = json.dumps([a.model_dump() for a in payload.ip_assets])

    profile = BusinessProfile(
        id=profile_id,
        company_name=payload.company_name,
        sector=payload.sector,
        company_type=payload.company_type,
        registration_number=payload.registration_number,
        state=payload.state,
        ip_assets_json=assets_json,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return _to_response(profile)


@router.get("/profile", response_model=List[BusinessProfileResponse], summary="List all Business Profiles")
async def list_profiles(db: AsyncSession = Depends(get_db)) -> List[BusinessProfileResponse]:
    """Retrieve all business profiles stored in SQLite."""
    result = await db.execute(select(BusinessProfile).order_by(BusinessProfile.updated_at.desc()))
    profiles = result.scalars().all()
    return [_to_response(p) for p in profiles]


@router.get("/profile/{profile_id}", response_model=BusinessProfileResponse, summary="Get Business Profile by ID")
async def get_profile(profile_id: str, db: AsyncSession = Depends(get_db)) -> BusinessProfileResponse:
    """Retrieve a specific business profile by ID."""
    profile = await db.get(BusinessProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business Profile with ID '{profile_id}' not found.",
        )
    return _to_response(profile)


@router.put("/profile/{profile_id}", response_model=BusinessProfileResponse, summary="Update Business Profile")
async def update_profile(profile_id: str, payload: BusinessProfileUpdate, db: AsyncSession = Depends(get_db)) -> BusinessProfileResponse:
    """Update company metadata or IP assets for an existing profile."""
    profile = await db.get(BusinessProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business Profile with ID '{profile_id}' not found.",
        )

    if payload.company_name is not None:
        profile.company_name = payload.company_name
    if payload.sector is not None:
        profile.sector = payload.sector
    if payload.company_type is not None:
        profile.company_type = payload.company_type
    if payload.registration_number is not None:
        profile.registration_number = payload.registration_number
    if payload.state is not None:
        profile.state = payload.state
    if payload.ip_assets is not None:
        profile.ip_assets_json = json.dumps([a.model_dump() for a in payload.ip_assets])

    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)

    return _to_response(profile)


# ---------------------------------------------------------------------------
# Derived Compliance Passport Endpoint
# ---------------------------------------------------------------------------


@router.get("/profile/{profile_id}/passport", response_model=CompliancePassportResponse, summary="Get Computed Compliance Passport")
async def get_compliance_passport(profile_id: str, db: AsyncSession = Depends(get_db)) -> CompliancePassportResponse:
    """
    Derive a computed 'Compliance Passport' summarizing the business's IP status,
    regulatory score, asset metrics, and actionable compliance checklist.
    """
    profile = await db.get(BusinessProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business Profile with ID '{profile_id}' not found.",
        )

    try:
        assets_raw = json.loads(profile.ip_assets_json or "[]")
        ip_assets = [IPAssetSchema(**a) for a in assets_raw]
    except Exception:
        ip_assets = []

    # 1. Count IP asset breakdown
    patents = [a for a in ip_assets if a.asset_type.lower() == "patent"]
    trademarks = [a for a in ip_assets if a.asset_type.lower() == "trademark"]
    copyrights = [a for a in ip_assets if a.asset_type.lower() == "copyright"]
    gis = [a for a in ip_assets if a.asset_type.lower() in {"gi", "geographical indication"}]

    breakdown = AssetBreakdown(
        patents_count=len(patents),
        trademarks_count=len(trademarks),
        copyrights_count=len(copyrights),
        gis_count=len(gis),
        total_assets=len(ip_assets),
    )

    # 2. Compute overall compliance score (0-100)
    score = 45  # Base starting score

    # Registration bonus
    if profile.registration_number and len(profile.registration_number.strip()) > 3:
        score += 15
    if profile.state:
        score += 5

    # Asset status scoring
    for a in ip_assets:
        st = a.status.lower()
        if st == "granted":
            score += 12
        elif st == "pending":
            score += 6
        elif st == "draft":
            score += 3

    # Sector specific bonuses
    is_ayush = profile.sector.upper() in {"AYUSH", "HERBAL", "AYURVEDA"}
    if is_ayush and len(patents) > 0:
        score += 10

    score = max(15, min(100, score))

    # 3. Determine status level
    if score >= 85:
        status_level = "EXCELLENT"
    elif score >= 70:
        status_level = "GOOD"
    elif score >= 50:
        status_level = "NEEDS_ATTENTION"
    else:
        status_level = "HIGH_RISK"

    # 4. Generate compliance checklist items
    checklist: List[ChecklistItem] = []

    # Item A: Registration Verification
    if profile.registration_number:
        checklist.append(
            ChecklistItem(
                item="Official Registration Number",
                status="PASSED",
                guidance=f"Registered under {profile.company_type} with ID: {profile.registration_number}.",
            )
        )
    else:
        checklist.append(
            ChecklistItem(
                item="Official Registration Number",
                status="WARNING",
                guidance="Missing UDYAM, CIN, or License number. Add for official verifiability.",
            )
        )

    # Item B: Sector Regulatory Compliance (AYUSH / Pharma / General)
    if is_ayush:
        checklist.append(
            ChecklistItem(
                item="AYUSH Rule 161 Labelling & Form 25-D",
                status="PASSED" if any(a.status.lower() == "granted" for a in ip_assets) else "WARNING",
                guidance="Ensure all OTC packaging explicitly states botanical names and manufacturing licence details.",
            )
        )
        checklist.append(
            ChecklistItem(
                item="Section 3(p) Patent Non-Eligibility Check",
                status="PASSED" if len(patents) > 0 else "WARNING",
                guidance="Ayurvedic formulations require novelty demonstration to clear Section 3(p) objections.",
            )
        )

    # Item C: Trademark Protection Check
    if len(trademarks) > 0:
        checklist.append(
            ChecklistItem(
                item="Brand & Logo Protection (Trademarks Act 1999)",
                status="PASSED",
                guidance=f"{len(trademarks)} trademark(s) recorded in profile.",
            )
        )
    else:
        checklist.append(
            ChecklistItem(
                item="Brand & Logo Protection (Trademarks Act 1999)",
                status="CRITICAL",
                guidance="No trademark filed. Risk of brand infringement under Section 29.",
            )
        )

    # Item D: Patent & Innovation Portfolio Check
    if len(patents) > 0:
        checklist.append(
            ChecklistItem(
                item="Patent Rights (Patents Act 1970)",
                status="PASSED" if any(p.status.lower() == "granted" for p in patents) else "WARNING",
                guidance=f"{len(patents)} patent file(s) logged in database.",
            )
        )
    else:
        checklist.append(
            ChecklistItem(
                item="Patent Rights (Patents Act 1970)",
                status="WARNING",
                guidance="Consider filing a provisional patent to protect proprietary formulations/processes.",
            )
        )

    # 5. Build recommended next actions
    actions: List[str] = []
    if not profile.registration_number:
        actions.append("Add your official UDYAM or CIN registration number to unlock statutory fee concessions.")

    if is_ayush and len(patents) == 0:
        actions.append("Perform a Section 3(p) patent eligibility audit for your flagship herbal formulation.")

    if len(trademarks) == 0:
        actions.append("Conduct a Class 5 / Class 35 trademark clearance search to protect your brand name.")

    if profile.company_type.lower() in {"startup", "msme"}:
        actions.append("Claim up to 80% rebate on official patent filing fees under the SIPP scheme.")

    if not actions:
        actions.append("Schedule a periodic IP audit to ensure timely renewal of granted patents and trademarks.")

    deadline = "Form 25-D Renewal due in 90 days" if is_ayush else "Annual IP Audit Due: Q4 2026"

    return CompliancePassportResponse(
        profile_id=profile.id,
        company_name=profile.company_name,
        sector=profile.sector,
        company_type=profile.company_type,
        overall_score=score,
        status_level=status_level,
        asset_breakdown=breakdown,
        compliance_checklist=checklist,
        recommended_actions=actions,
        next_filing_deadline=deadline,
    )
