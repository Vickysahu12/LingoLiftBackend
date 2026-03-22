from pydantic import BaseModel
from typing import Optional, List
import uuid

class VAQuestionResponse(BaseModel):
    id:            uuid.UUID
    question_type: str
    question:      str
    options:       List[dict] = []
    strategy:      Optional[dict] = None
    difficulty:    str
    sentences:     Optional[List[dict]] = None  # ← ye add karo
    model_config   = {"from_attributes": True}

class VASubmitRequest(BaseModel):
    question_id:   uuid.UUID
    question_type: str
    selected:      Optional[str] = None  # "A", "B", "C", "D"

class VASubmitResponse(BaseModel):
    is_correct:    bool
    correct:       str
    explanation:   Optional[dict] = None

class VAHubResponse(BaseModel):
    user_name:     str
    streak:        int
    total_progress: float
    modules: List[dict]  # [{id, title, progress, tag}]

class VAProgressResponse(BaseModel):
    pj_attempted:   int
    pj_correct:     int
    ooo_attempted:  int
    ooo_correct:    int
    ps_attempted:   int
    ps_correct:     int
    total_attempted: int
    total_correct:  int
    accuracy:       float
    model_config    = {"from_attributes": True}

# Admin
class VAOptionCreate(BaseModel):
    id:        str          # "A", "B", "C", "D"
    text:      str
    highlight: Optional[str] = None

class VAQuestionCreate(BaseModel):
    question_type: str      # 'para_jumble' | 'odd_one_out' | 'para_summary'
    question:      str
    options:       List[VAOptionCreate]
    correct:       str      # "A", "B", "C", "D"
    explanation:   dict     # {"correct": "A", "why": "..."}
    sentences: Optional[List[dict]] = None  # ← ye add karo
    strategy:      Optional[dict] = None
    difficulty:    str = "Medium"
    order_index:   int = 0