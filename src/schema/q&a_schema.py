## q&a_schema.py
# import
from pydantic import BaseModel, Field
from typing import List

class QASource(BaseModel):
    docuemnt_id: str
    page: int
    justification: str


class QAResult(BaseModel):
    answer: str
    sources: List[QASource] = Field(default_factory=list)
    confidence: float