## decision_llm.py
# imports
import json
from openai import OpenAI
from pydantic import ValidationError

from src.schema.decision_schema import LLMDecisionResult
from src.schema.aggregation_schema import LLMAggregatedResult
from src.agent.prompts import DECISION_PROMPT
import src.utils.llm_helper as llm
import src.utils.file_helper as fh
from src.core.memory import Session


#########
# HELPER
#########
def normalize_decision_output(data: dict):
    logger = Session.logger
    
    list_fields = [
        "key_conclusions",
        "main_risks",
        "recommendations",
        "research_priority",
    ]

    for field in list_fields:
        if field in data:
            if isinstance(data[field], str):
                data[field] = [data[field]]
                logger.warning(f"{field} was string → converted to list")

    return data


########
# MAIN 
########
class LLMDecisionEngine:
    def __init__(self, llm_config):
        self.client = OpenAI()
        self.model = llm_config["model"]
        self.temperature = float(llm_config["temperature"])
        self.namespace = llm_config["namespace"]
        self.max_retries = llm_config["max_retries"]

    def decide(self, agg_input: LLMAggregatedResult | dict):
        logger = Session.logger

        if isinstance(agg_input, dict):
            agg_input_str = json.dumps(agg_input, indent=2)
        elif isinstance(agg_input, LLMAggregatedResult):
            agg_input_str = agg_input.model_dump_json(indent=2)
        else:
            raise TypeError(f"'agg_input' must be of type 'dict' or '', not: ", 
                            type(agg_input))

        prompt = DECISION_PROMPT.replace("{TEXT}", agg_input_str)

        key = llm._make_cache_key(
            agg_input_str,
            prompt,
            self.namespace + "_decision"
            )

        info = {
            "prompt_decision": prompt,
            "key_decision": key
            }
        
        cached = llm._load_from_cache(key)

        
        for attempt in range(3):
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
                    data = fh.safe_json_loads(cleaned_output)
                    # except json.JSONDecodeError:
                    #     raise ValueError(f"Invalid JSON from LLM decision:\n{cleaned_output}")
                
                except Exception as e_load:
                    logger.error("[Retry %s] invalid JSON when loading:\n%s", 
                                 attempt,
                                 e_load)

            try:
                data = normalize_decision_output(data)
                validated = LLMDecisionResult(**data)
                llm._save_to_cache(key, data)

                return validated, info
                
            except Exception as e_convert:
                logger.error("[Retry %s] invalid JSON when converting:\n%s", 
                             attempt,
                             e_convert)
                    # raise ValueError(f"LLM aggregation schema validation failed:\n{e}")

            
    
        raise ValueError("LLM failed to produce valid JSON after retries")
        
