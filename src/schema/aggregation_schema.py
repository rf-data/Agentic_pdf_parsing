## 
# import
from pydantic import BaseModel, Field
from typing import List, Literal


class AggregatedResult(BaseModel):
    common_entities: List[str]
    unique_entities: List[str]

    common_mechanisms: List[str]
    dominant_mechanisms: List[str]

    common_findings: List[str]
    conflicting_findings: List[str]

    overall_quality: str
    summary: str


class LLMAggregatedResult(BaseModel):
    document_set_topic: str = Field(
        ...,
        description="Main overarching topic across the document set"
    )

    consensus_points: List[str] = Field(
        default_factory=list,
        description="Semantically grouped points supported by multiple documents"
    )

    conflicting_points: List[str] = Field(
        default_factory=list,
        description="Findings that appear inconsistent or point in different directions"
    )

    dominant_mechanisms: List[str] = Field(
        default_factory=list,
        description="Most relevant biological or scientific mechanisms across documents"
    )

    subgroup_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested document groupings for better comparison"
    )

    evidence_gaps: List[str] = Field(
        default_factory=list,
        description="Areas where more documents or more specific evidence are needed"
    )

    overall_interpretation: str = Field(
        ...,
        description="High-level synthesis of the document set"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the aggregation quality"
    )
"""
class AggregatedResult(BaseModel):
    n_documents: int
    titles: List[str]

    unique_entities: List[str]
    common_entities: List[str]

    unique_mechanisms: List[str]
    common_mechanisms: List[str]
    dominant_mechanisms: List[str]

    unique_findngs: List[str]
    common_findings: List[str]
    conflicting_findings: List[str]

    methods: List[str]

    unique_qualities: List[str]
    overall_quality: str

    summary: str
"""