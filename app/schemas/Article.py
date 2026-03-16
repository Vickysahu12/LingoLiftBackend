from pydantic import BaseModel
from typing import Optional, List
import uuid

class ArticleAnalysisResponse(BaseModel):
    score:        int
    difficulty:   str
    central_idea: Optional[str] = None
    tone:         Optional[dict] = None
    structure:    List[dict] = []
    arguments:    List[dict] = []
    cat_tip:      Optional[str] = None
    model_config  = {"from_attributes": True}

class ArticleListItem(BaseModel):
    id:            uuid.UUID
    title:         str
    tag:           Optional[str] = None
    meta:          Optional[str] = None
    level:         str
    image_url:     Optional[str] = None
    is_bookmarked: bool = False
    is_read:       bool = False
    model_config   = {"from_attributes": True}

class ArticleDetailResponse(BaseModel):
    id:            uuid.UUID
    title:         str
    tag:           Optional[str] = None
    meta:          Optional[str] = None
    level:         str
    content:       List[str] = []
    image_url:     Optional[str] = None
    is_bookmarked: bool = False
    is_read:       bool = False
    analysis:      Optional[ArticleAnalysisResponse] = None
    model_config   = {"from_attributes": True}

# Requests
class ArticleTimeTrack(BaseModel):
    seconds_spent: int

class ArticleCreate(BaseModel):
    title:       str
    tag:         Optional[str] = None
    meta:        Optional[str] = None
    level:       str = "Medium"
    content:     List[str] = []
    image_url:   Optional[str] = None
    order_index: int = 0

class ArticleAnalysisCreate(BaseModel):
    score:        int = 0
    difficulty:   str = "Medium"
    central_idea: Optional[str] = None
    tone:         Optional[dict] = None
    structure:    List[dict] = []
    arguments:    List[dict] = []
    cat_tip:      Optional[str] = None