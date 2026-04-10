## extraction.py
# imports
import json
from openai import OpenAI
from pydantic import ValidationError

from src.schema.extraction_schema import ExtractedDocument
from src.agent.prompts import EXTRACTION_PROMPT
import src.utils.llm_helper as llm


class ExtractionEngine:
    def __init__(self, llm_config):
        self.client = OpenAI()
        self.model = llm_config["model"]    # "gpt-4o-mini"model
        self.temperature = float(llm_config["temperature"])
        self.namespace = llm_config["namespace"]
        self.max_retries = llm_config["max_retries"]

    def extract_info_with_retry(self, text: str):
         
        for i in range(self.max_retries):
            try:
                return self.extract_info(text)
            except Exception as e:
                print(f"[Retry {i+1}] {e}")

        raise RuntimeError("Extraction failed after retries")

 
    def extract_info(self, text: str) -> ExtractedDocument:
        prompt = EXTRACTION_PROMPT.replace("{TEXT}", text[:8000])  # safety cut

        key = llm._make_cache_key(
                        text, 
                        prompt, 
                        self.namespace
                        )
        
        info = {
            "prompt_extraction": prompt,
            "key_extraction": key
            }
        
        cached = llm._load_from_cache(key)

        if cached is not None:
            data = cached
        
        else:
            response = self.client.chat.completions.create(
                                                    model=self.model,
                                                    temperature=self.temperature,
                                                    messages=[
                                                        {"role": "user", 
                                                        "content": prompt}
                                                        ]
                                                    )

            raw_output = response.choices[0].message.content.strip()
            cleaned_output = llm._clean_llm_output(raw_output)
    
            try:
                data = json.loads(cleaned_output)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON from LLM extraction:\n{cleaned_output}")

        try:
            validated = ExtractedDocument(**data)
        except ValidationError as e:
            raise ValueError(f"LLM extraction schema validation failed:\n{e}")

        llm._save_to_cache(key, data)

        return validated, info