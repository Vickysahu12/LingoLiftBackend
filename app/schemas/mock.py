from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
import uuid
from datetime import datetime
from app.models.mock import MockType, DifficultyLevel, BadgeType, QuestionType, AttemptStatus, QuestionStatus


# ─────────────────────────────────────────────────────────────────────────────
# LIST SCREEN  →  GET /mocks/
# Maps to MOCK_DATA in MockListScreen.jsx
# ─────────────────────────────────────────────────────────────────────────────

class MockListItem(BaseModel):
    id:              uuid.UUID
    title:           str
    subtitle:        Optional[str]    = None
    type:            MockType
    icon:            str              = "📋"
    badge:           Optional[BadgeType] = None
    difficulty:      DifficultyLevel
    total_questions: int
    duration:        str                          # "40 Minutes"
    max_score:       int
    attempts:        Optional[str]    = None      # "1.2k" formatted string
    topics:          List[str]        = []

    # User-specific (injected by service)
    is_attempted:    bool             = False
    last_score:      Optional[int]    = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# DETAIL SCREEN  →  GET /mocks/{mock_id}
# Maps to MOCK_DETAILS[id] in MockDetailScreen.jsx
# ─────────────────────────────────────────────────────────────────────────────

class MarkingSchemeOut(BaseModel):
    correct:      str           # "+3 Marks"
    correct_sub:  str
    wrong:        str           # "-1 Mark"
    wrong_sub:    str
    tita:         str           # "0 Marks" or "N/A"
    tita_sub:     str
    has_tita:     bool
    model_config = {"from_attributes": True}

class MockSectionOut(BaseModel):
    id:           uuid.UUID
    section_key:  str
    label:        str
    icon:         str
    duration:     str
    questions:    int
    breakdown:    Optional[str] = None
    color:        str
    is_locked:    bool
    model_config = {"from_attributes": True}

class MockRuleOut(BaseModel):
    icon:  str
    label: str
    model_config = {"from_attributes": True}

class MockSyllabusOut(BaseModel):
    label:   str
    covered: bool
    model_config = {"from_attributes": True}

class MockDetailResponse(BaseModel):
    id:               uuid.UUID
    title:            str
    subtitle:         Optional[str]       = None
    description:      Optional[str]       = None
    type:             MockType
    icon:             str
    badge:            Optional[BadgeType] = None
    difficulty:       DifficultyLevel
    total_duration:   str
    duration_secs:    int
    total_questions:  int
    max_score:        int
    sections:         List[MockSectionOut] = []
    marking:          Optional[MarkingSchemeOut] = None
    rules:            List[MockRuleOut]    = []
    syllabus:         List[MockSyllabusOut]= []
    instructions:     List[str]            = []

    # User-specific
    attempt_number:   int                  = 1    # next attempt number
    is_attempted:     bool                 = False
    last_score:       Optional[int]        = None
    last_attempt_id:  Optional[uuid.UUID]  = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# TEST INTERFACE  →  GET /mocks/{mock_id}/exam-config
# Maps to getExamData(mockId) in examData.js
# ─────────────────────────────────────────────────────────────────────────────

class PassageOut(BaseModel):
    id:          uuid.UUID
    passage_key: str
    label:       Optional[str] = None
    title:       Optional[str] = None
    content:     List[str]     = []
    model_config = {"from_attributes": True}

class QuestionOut(BaseModel):
    id:             uuid.UUID
    number:         int
    type:           QuestionType
    text:           str
    options:        Optional[List[str]] = None
    hint:           Optional[str]       = None
    passage_id:     Optional[str]       = None   # passage_key string (frontend uses this)
    marks: dict = {"correct": 3, "incorrect": -1}
    model_config = {"from_attributes": True}

    # NOTE: correct_option and correct_answer are NOT included here
    # They are only returned in /solutions endpoint after submit

class ExamSectionOut(BaseModel):
    id:              uuid.UUID
    section_key:     str
    label:           str
    icon:            str
    total_questions: int
    duration_secs:   int
    is_locked:       bool
    passages:        List[PassageOut]   = []
    questions:       List[QuestionOut] = []
    model_config = {"from_attributes": True}

class ExamConfigResponse(BaseModel):
    mock_id:      uuid.UUID
    test_title:   str
    subject:      str              = "VARC"
    total_seconds: int
    sections:     List[ExamSectionOut] = []
    # attempt_id returned so frontend can save responses mid-test
    attempt_id:   uuid.UUID
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# SUBMIT  →  POST /attempts/{attempt_id}/submit
# Frontend sends questionMeta + timeTaken, gets back result
# ─────────────────────────────────────────────────────────────────────────────

class QuestionMetaIn(BaseModel):
    """Single question state from frontend questionMeta object"""
    status:       QuestionStatus
    selected:     Optional[int]   = None    # option index
    tita_answer:  Optional[str]   = None
    time_spent:   Optional[int]   = 0       # seconds on this question

class SubmitAttemptRequest(BaseModel):
    # key = question UUID string, value = meta
    question_meta: dict[str, QuestionMetaIn]
    time_taken_secs: int

class SectionResultOut(BaseModel):
    total:       int
    correct:     int
    wrong:       int
    unattempted: int
    attempted:   int
    score:       int
    max_score:   int
    accuracy:    float

class SubmitAttemptResponse(BaseModel):
    attempt_id:   uuid.UUID
    mock_id:      uuid.UUID
    status:       AttemptStatus

    score:        int
    max_score:    int
    correct:      int
    wrong:        int
    unattempted:  int
    attempted:    int
    accuracy:     float
    time_taken_secs: int

    rc_result:    Optional[SectionResultOut] = None
    va_result:    Optional[SectionResultOut] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# SOLUTIONS  →  GET /attempts/{attempt_id}/solutions
# Maps to SolutionScreen.jsx — returns question + user answer + correct answer
# ─────────────────────────────────────────────────────────────────────────────

class QuestionSolutionOut(BaseModel):
    id:             uuid.UUID
    number:         int
    type:           QuestionType
    text:           str
    options:        Optional[List[str]] = None
    correct_option: Optional[int]       = None    # NOW revealed
    correct_answer: Optional[str]       = None    # for TITA
    hint:           Optional[str]       = None
    explanation:    Optional[str]       = None
    key_point:      Optional[str]       = None
    passage_id:     Optional[str]       = None    # passage_key
    marks:          dict = {"correct": 3, "incorrect": -1}

    # User's response
    user_status:    QuestionStatus
    user_selected:  Optional[int]       = None
    user_tita:      Optional[str]       = None
    is_correct:     Optional[bool]      = None

    model_config = {"from_attributes": True}

class SolutionSectionOut(BaseModel):
    section_key: str
    label:       str
    passages:    List[PassageOut]         = []
    questions:   List[QuestionSolutionOut]= []
    model_config = {"from_attributes": True}

class SolutionsResponse(BaseModel):
    attempt_id:  uuid.UUID
    mock_id:     uuid.UUID
    test_title:  str
    sections:    List[SolutionSectionOut] = []
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# USER ATTEMPT HISTORY  →  GET /mocks/{mock_id}/attempts  (my attempts)
# ─────────────────────────────────────────────────────────────────────────────

class AttemptHistoryItem(BaseModel):
    attempt_id:      uuid.UUID
    attempt_number:  int
    status:          AttemptStatus
    score:           int
    max_score:       int
    accuracy:        float
    time_taken_secs: int
    submitted_at:    Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# SAVE PROGRESS (mid-test)  →  POST /attempts/{attempt_id}/save
# Frontend can auto-save every 30s to not lose progress
# ─────────────────────────────────────────────────────────────────────────────

class SaveProgressRequest(BaseModel):
    question_meta:   dict[str, QuestionMetaIn]
    time_taken_secs: int