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
You are an information extraction system.

"""
