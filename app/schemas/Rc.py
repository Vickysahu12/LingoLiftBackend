from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class RCOptionResponse(BaseModel):
    id:          uuid.UUID
    option_text: str
    order_index: int
    model_config = {"from_attributes": True}

class RCQuestionResponse(BaseModel):
    id:          uuid.UUID
    question:    str
    difficulty:  str
    analysis:    Optional[str] = None
    order_index: int
    options:     List[RCOptionResponse] = []
    model_config = {"from_attributes": True}

class RCPassageResponse(BaseModel):
    id:         uuid.UUID
    title:      str
    body:       str
    subject:    str
    difficulty: str
    source:     Optional[str] = None
    questions:  List[RCQuestionResponse] = []
    model_config = {"from_attributes": True}

class RCPassageListItem(BaseModel):
    id:         uuid.UUID
    title:      str
    subject:    str
    difficulty: str
    source:     Optional[str] = None
    total_questions: int = 0
    model_config = {"from_attributes": True}

# Submit attempt
class RCAnswerSubmit(BaseModel):
    question_id:    uuid.UUID
    selected_index: Optional[int] = None  # None = skipped
    correct_index:  int

class RCAttemptSubmit(BaseModel):
    passage_id:  uuid.UUID
    answers:     List[RCAnswerSubmit]
    time_taken:  int  # seconds

# Result response
class RCAttemptResult(BaseModel):
    attempt_id:  uuid.UUID
    score:       float
    correct:     int
    wrong:       int
    skipped:     int
    time_taken:  int
    total:       int

# Admin
class RCOptionCreate(BaseModel):
    option_text: str
    is_correct:  bool
    order_index: int

class RCQuestionCreate(BaseModel):
    question:    str
    difficulty:  str = "Medium"
    analysis:    Optional[str] = None
    order_index: int = 0
    options:     List[RCOptionCreate]

class RCPassageCreate(BaseModel):
    title:       str
    body:        str
    subject:     str = "Reading Comprehension"
    difficulty:  str = "Medium"
    source:      Optional[str] = None
    order_index: int = 0
    questions:   List[RCQuestionCreate] = []