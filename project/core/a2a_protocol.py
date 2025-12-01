"""
Agent-to-Agent communication data structures.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

@dataclass
class PlannerOutput:
    emotion: str
    risk_level: str
    distress_score: int
    action: str
    instruction: str
    technique_suggestion: str
    needs_validation: bool
    # NEW: Field to capture preferences for long-term memory
    save_preference: Optional[Dict[str, str]] = None 

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WorkerOutput:
    draft_response: str
    tools_used: List[str]
    technique_applied: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvaluatorOutput:
    status: str
    feedback: str
    final_response: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)