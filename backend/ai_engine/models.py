from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Issue(BaseModel):
    tag: str
    level: str = Field(..., description="e.g. 'critical', 'warning'")
    coach_tip: Dict[str, str]
    suggestion: Dict[str, str]

class AnalysisResult(BaseModel):
    action: str
    level_assumption: str
    score: int
    metrics: Dict[str, float]
    issues: List[Issue]
    positive_feedback: Dict[str, str]
    next_training_focus: List[Dict[str, str]]
    keyframe_base64: Optional[str] = None
    generation_source: str = "rules" # "rules" or "gemini"
