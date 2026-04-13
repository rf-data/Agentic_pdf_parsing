## decision_schema.py
# imports
from pydantic import BaseModel
from typing import List


class DecisionResult(BaseModel):
    confidence_level: str                 # low / medium / high
    evidence_strength: str               # weak / moderate / strong

    key_conclusions: List[str]
    risks: List[str]

    recommendations: List[str]

    reasoning: str


class LLMDecisionResult(BaseModel):
    key_conclusions: List[str]
    main_risks: List[str]
    recommendations: List[str]

    research_priority: List[str]

    confidence: float
    reasoning: str