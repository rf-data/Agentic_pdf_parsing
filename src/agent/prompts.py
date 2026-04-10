## prompts.py
# imports


EXTRACTION_PROMPT = """
You are an information extraction system.

Extract structured information from the following scientific text.

Return ONLY valid JSON. No explanation.

Schema:
{
  "title": string,
  "category": "research_paper" | "review" | "clinical" | "other",
  "summary": string,
  "key_entities": [string],
  "key_findings": [string],
  "methods": [string],
  "main_topics": [string],
  "mechanisms": [string],
  "outcomes": [string],
  "missing_fields": [string],
  "review_flags": [string],
  "quality_assessment":  "low" | "medium" | "high",
  "confidence": float (0.0 - 1.0)
}

Rules:
- Be concise and factual
- Do not hallucinate
- If unsure → leave empty list
- Confidence reflects extraction reliability
- Only infer missing information if strongly supported
- Do not speculate

Text:
\"\"\"
{TEXT}
\"\"\"
"""


AGGREGATION_PROMPT = """
You are a scientific aggregation system.

You receive (1) structured extraction results from multiple 
scientific documents (source of truth) and (2) a deterministic 
pre-aggregation (secondary signal). 
Your task is to aggregate them semantically.

Return ONLY valid JSON. No explanation.

Schema:
{
  "document_set_topic": string,
  "consensus_points": [string],
  "conflicting_points": [string],
  "dominant_mechanisms": [string],
  "subgroup_suggestions": [string],
  "evidence_gaps": [string],
  "overall_interpretation": string,
  "confidence": float
}

Rules on extraction results:
- Group semantically similar findings together
- Do not repeat slightly reworded statements separately
- Only label something as conflict if the documents genuinely point in different directions
- Suggest subgroups when documents appear to differ in scope, mechanism, disease context, or methodology
- If evidence is too limited, explicitly mention that in evidence_gaps
- Be concise and factual
- Do not speculate

Rules on pre-aggregation:
- The pre-aggregation may be incomplete or incorrect
- You MUST critically evaluate and refine it
- Do NOT blindly copy it

Structured document data:
\"\"\"
{TEXT}
\"\"\"
"""
