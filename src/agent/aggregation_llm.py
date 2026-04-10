## aggregation_llm.py
# imports
# from collections import Counter
# from typing import List

# from src.schema.extraction_schema import ExtractedDocument
# from src.schema.aggregation_schema import AggregatedResult
# from src.core.session import session

import json
from openai import OpenAI
from pydantic import ValidationError

from src.schema.aggregation_schema import LLMAggregatedResult
from src.agent.prompts import AGGREGATION_PROMPT
import src.utils.llm_helper as llm



# ------------------
# MAIN FUNCTION
# ------------------

class LLMAggregationEngine:
    def __init__(self, llm_config):
        self.client = OpenAI()
        self.model = llm_config["model"]
        self.temperature = float(llm_config["temperature"])
        self.namespace = llm_config["namespace"]
        self.max_retries = llm_config["max_retries"]

    def aggregate_with_retry(self, structured_input: str):
        for i in range(self.max_retries):
            try:
                return self.aggregate(structured_input)
            except Exception as e:
                print(f"[LLM Aggregation Retry {i+1}] {e}")

        raise RuntimeError("LLM aggregation failed after retries")

    def aggregate(self, structured_input: str):
        prompt = AGGREGATION_PROMPT.replace("{TEXT}", structured_input[:12000])

        key = llm._make_cache_key(
            structured_input,
            prompt,
            self.namespace + "_aggregation"
        )

        info = {
            "prompt_aggregation": prompt,
            "key_aggregation": key
        }

        cached = llm._load_from_cache(key)

        if cached is not None:
            data = cached
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            raw_output = response.choices[0].message.content.strip()
            cleaned_output = llm._clean_llm_output(raw_output)

            try:
                data = json.loads(cleaned_output)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON from LLM aggregation:\n{cleaned_output}")

        try:
            validated = LLMAggregatedResult(**data)
        except ValidationError as e:
            raise ValueError(f"LLM aggregation schema validation failed:\n{e}")

        llm._save_to_cache(key, data)

        return validated, info