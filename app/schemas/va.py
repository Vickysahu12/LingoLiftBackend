from pydantic import BaseModel
from typing import Optional, List
import uuid


# ─── Shared ───────────────────────────────────────────────────────────────────

class VASentence(BaseModel):
    """Unified sentence format for para_jumble and odd_one_out."""
    id: str        # "A", "B", "C", "D", "E"
    text: str


class VAOptionCreate(BaseModel):
    id: str                        # "A", "B", "C", "D"
    text: str
    highlight: Optional[str] = None


# ─── Admin: Create ─────────────────────────────────────────────────────────────

class VAQuestionCreate(BaseModel):
    question_type: str             # 'para_jumble' | 'odd_one_out' | 'para_summary'
    question: str
    options: List[VAOptionCreate]
    correct: str                   # "A", "B", "C", "D"
    explanation: dict              # {"why": "..."}
    sentences: Optional[List[VASentence]] = None   # para_jumble / odd_one_out only
    strategy: Optional[dict] = None
    difficulty: str = "Medium"
    order_index: int = 0


# ─── Admin: Update (partial) ───────────────────────────────────────────────────

class VAQuestionUpdate(BaseModel):
    question_type: Optional[str] = None
    question: Optional[str] = None
    options: Optional[List[VAOptionCreate]] = None
    correct: Optional[str] = None
    explanation: Optional[dict] = None
    sentences: Optional[List[VASentence]] = None
    strategy: Optional[dict] = None
    difficulty: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


# ─── Admin: Reorder ───────────────────────────────────────────────────────────

class VAReorderRequest(BaseModel):
    ordered_ids: List[uuid.UUID]   # IDs in new order, index = new order_index


# ─── Admin: List Response ─────────────────────────────────────────────────────

class VAQuestionAdminItem(BaseModel):
    id: uuid.UUID
    question_type: str
    question: str
    options: List[dict]
    sentences: Optional[List[dict]] = None
    correct: str
    explanation: Optional[dict] = None
    strategy: Optional[dict] = None
    difficulty: str
    is_active: bool
    order_index: int

    model_config = {"from_attributes": True}


class VAQuestionAdminListResponse(BaseModel):
    items: List[VAQuestionAdminItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─── User: Question Response ──────────────────────────────────────────────────

class VAQuestionResponse(BaseModel):
    id: uuid.UUID
    question_type: str
    question: str
    options: List[dict] = []
    sentences: Optional[List[dict]] = None
    strategy: Optional[dict] = None
    difficulty: str

    model_config = {"from_attributes": True}


# ─── User: Submit ─────────────────────────────────────────────────────────────

class VASubmitRequest(BaseModel):
    question_id: uuid.UUID
    question_type: str
    selected: Optional[str] = None    # "A", "B", "C", "D"


class VASubmitResponse(BaseModel):
    is_correct: bool
    correct: str
    explanation: Optional[dict] = None


# ─── User: Hub ────────────────────────────────────────────────────────────────

class VAHubResponse(BaseModel):
    user_name: str
    streak: int
    total_progress: float
    modules: List[dict]


# ─── User: Progress ───────────────────────────────────────────────────────────

class VAProgressResponse(BaseModel):
    pj_attempted: int
    pj_correct: int
    ooo_attempted: int
    ooo_correct: int
    ps_attempted: int
    ps_correct: int
    total_attempted: int
    total_correct: int
    accuracy: float

    model_config = {"from_attributes": True}