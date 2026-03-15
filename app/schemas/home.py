from pydantic import BaseModel
from typing import List, Optional

class PracticeStats(BaseModel):
    vocab:   dict  # {done: int, total: int}
    rc:      dict  # {passages: int}
    va:      dict  # {types: str}

class TestStats(BaseModel):
    rc:    dict  # {label: str}
    va:    dict  # {label: str}

class HomeStatsResponse(BaseModel):
    name:           str
    day_count:      int     # kitne din se app use kar raha hai
    streak:         int
    study_time:     str     # "4h 20m" format
    today_progress: float   # 0-100
    practice_stats: PracticeStats
    test_stats:     TestStats
    week_activity:  List[bool]  # [Mon-Sun]

class PracticeModule(BaseModel):
    id:          str
    title:       str
    description: str
    progress:    float
    tag:         Optional[str] = None

class PracticeModulesResponse(BaseModel):
    modules:       List[PracticeModule]
    goal_completed: int
    goal_total:     int
    streak:         int