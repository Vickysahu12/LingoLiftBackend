from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

# ─── Vocab Word ───────────────────────────────────────────
class VocabWordResponse(BaseModel):
    id:          uuid.UUID
    word:        str
    phonetic:    Optional[str] = None
    definition:  str
    synonyms:    List[str] = []
    antonyms:    List[str] = []
    context:     Optional[str] = None
    source:      Optional[str] = None
    article_url: Optional[str] = None
    tip:         Optional[str] = None
    tag:         Optional[str] = None
    is_completed: bool = False
    is_bookmarked: bool = False

    model_config = {"from_attributes": True}

# ─── Quiz ─────────────────────────────────────────────────
class VocabQuizResponse(BaseModel):
    word_id:     uuid.UUID
    word:        str
    phonetic:    Optional[str] = None
    question:    str
    options:     List[str]
    explanation: Optional[str] = None

class VocabQuizSubmit(BaseModel):
    word_id:     uuid.UUID
    selected:    int   # index of selected option (0-3)
    correct:     int   # index of correct option

class VocabQuizResult(BaseModel):
    is_correct:  bool
    explanation: Optional[str] = None
    correct_index: int

# ─── Bookmark ─────────────────────────────────────────────
class BookmarkToggleRequest(BaseModel):
    word_id: uuid.UUID

class BookmarkToggleResponse(BaseModel):
    is_bookmarked: bool
    message: str

# ─── Progress ─────────────────────────────────────────────
class VocabProgressResponse(BaseModel):
    total_words:     int
    completed_words: int
    bookmarked_words: int
    accuracy:        float  # percentage

# ─── Admin Upload ──────────────────────────────────────────
class VocabWordCreate(BaseModel):
    word:        str
    phonetic:    Optional[str] = None
    definition:  str
    synonyms:    List[str] = []
    antonyms:    List[str] = []
    context:     Optional[str] = None
    source:      Optional[str] = None
    article_url: Optional[str] = None
    tip:         Optional[str] = None
    tag:         Optional[str] = None
    order_index: int = 0