##
# import
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ExtractedDocument(BaseModel):
    title: str = Field(..., description="Title or main topic of the document")

    category: Literal[
                "research_paper",
                "review",
                "clinical",
                "other"
                ]

    summary: str = Field(..., description="Short summary (5-10 sentences)")

    key_entities: List[str] = Field(
                                default_factory=list,
                                description="Important biomedical entities"
                                )
    
    key_findings: List[str] = Field(
                                default_factory=list,
                                description="Main findings or claims"
                                )

    methods: List[str] = Field(
                            default_factory=list,
                            description="Methods used in the study"
                            )

    main_topics: List[str] = Field(
        default_factory=list,
        description="Core scientific topics"
    )

    mechanisms: List[str] = Field(
        default_factory=list,
        description="Biological or pharmacological mechanisms"
    )

    outcomes: List[str] = Field(
        default_factory=list,
        description="Main outcomes or conclusions"
    )

    missing_fields: List[str] = Field(
                        default_factory=list,
                        description="Potentially missing aspects inferred from the text"   
                        )
    
    review_flags: List[str] = Field(
                        default_factory=list,
                        description="Potential issues or limitations identified in the document"
                        )
    
    quality_assessment: Literal[
                            "high",
                            "medium",
                            "low"
                            ] = None

    confidence: float = Field(
                            ...,
                            ge=0.0,
                            le=1.0,
                            description="Model confidence in extraction"
                            )

#     missing_fields: List[str] = []
#     confidence: float = Field(ge=0.0, le=1.0)
#     needs_review: bool
#     next_action: str


# class ExtractionResult(BaseModel):
#     document_type: str
#     key_entities: list[str]
#     summary: str
#     important_dates: list[str]
#     missing_fields: list[str]
#     confidence: float


# class AgentResult(BaseModel):
#     file_name: str
#     extraction: ExtractionResult
#     needs_review: bool
#     next_action: str
#     decision_reason: str