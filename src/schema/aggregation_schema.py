## 
# import
from pydantic import BaseModel, Field
from typing import List


class AggregatedResult(BaseModel):
    common_entities: List[str]
    unique_entities: List[str]

    common_mechanisms: List[str]
    dominant_mechanisms: List[str]

    common_findings: List[str]
    conflicting_findings: List[str]

    overall_quality: str

    summary: str

