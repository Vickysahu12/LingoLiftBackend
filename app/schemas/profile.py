from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import uuid


# ─── STATS (computed, not stored) ────────────────────────────────────────────

class UserStatsOut(BaseModel):
    streak:      int   = 0
    tests_given: int   = 0
    avg_score:   float = 0.0
    rank:        int   = 0


# ─── SUBSCRIPTION (placeholder — v2 mein full table banega) ──────────────────

class SubscriptionOut(BaseModel):
    plan:       str  = "Free"
    expires_at: Optional[str] = None
    is_active:  bool = False


# ─── PROFILE RESPONSE  →  GET /user/profile ──────────────────────────────────
# Maps exactly to MOCK_USER shape in ProfileScreen.jsx

class ProfileResponse(BaseModel):
    id:          uuid.UUID
    name:        str
    email:       str
    phone:       Optional[str]  = None
    avatar_url:  Optional[str]  = None   # profile_pic field from User model
    target_exam: Optional[str]  = None
    target_year: Optional[str]  = None
    stats:        UserStatsOut
    subscription: SubscriptionOut

    model_config = {"from_attributes": True}


# ─── UPDATE PROFILE REQUEST  →  PUT /user/profile ────────────────────────────

class UpdateProfileRequest(BaseModel):
    name:        Optional[str] = None
    phone:       Optional[str] = None
    target_exam: Optional[str] = None
    target_year: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and len(v.replace(" ", "").replace("+", "")) < 10:
            raise ValueError("Invalid phone number")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError("Name too short")
        return v.strip() if v else v


# ─── UPDATE PROFILE RESPONSE ─────────────────────────────────────────────────

class UpdateProfileResponse(BaseModel):
    success:     bool = True
    name:        str
    phone:       Optional[str] = None
    target_exam: Optional[str] = None
    target_year: Optional[str] = None
    model_config = {"from_attributes": True}