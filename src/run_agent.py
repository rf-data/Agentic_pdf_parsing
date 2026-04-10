## run_agent.py
# import
import click
import os
from datetime import datetime


from src.agent.extraction import ExtractionEngine
from src.agent.aggregation import AggregationEngine
from src.agent.aggregation_llm import LLMAggregationEngine
from src.agent.decision import DecisionEngine
from src.core.session import session
from src.core.logger import create_logger
# from src.schema.extraction_schema import ExtractedDocument
import src.tools.text_extraction as extract

import src.utils.general_helper as gh
import src.utils.llm_helper as llm
import src.utils.file_helper as fh
# import get_yaml_config


# ------------------
# MAIN FUNCTION
# ------------------

@click.command()
@click.option("--config_name", prompt="Name of 'config_file' (no suffix)",
              help='The config_file to use.')
def agentic_text_parsing(config_name):  
    
    return run_agentic_text_parsing(config_name)

def run_agentic_text_parsing(config_name: str):
    # load env variables and config
    gh.load_env_vars()
    data_raw = os.getenv("DATA_RAW")
    data_processed = os.getenv("DATA_PROCESSED")
    
    config = fh.get_yaml_config(config_name)
    general_config = config.get("general_args", {})
    file_name = general_config["file_name"]
    log_name = general_config["name_log"]
    name_logfile = general_config["name_logfile"]

    llm_config = config.get("llm_settings", {})
    
    # setup logger
    logger = create_logger(name=log_name, file_name=name_logfile)
    session.logger = logger

    # extract text from pdf + cleaning
    now = "2026-04-10_11-59-06" 
    # now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session.now = now

    if isinstance(file_name, str):
        file_name = [file_name]
    
    texts = {}
    settings = {
            "llm_config": llm_config
            }
    
    for name in file_name:
        logger.info("Start extracting text from file:\t%s",
                    name)
        name_short = name.split(".")[0]

        f_path = f"{data_raw}/{name}"
        cleaned_text, info = extract.extract_text_per_page(f_path, save=False)

        settings.update(info)
        texts[name_short] = str(cleaned_text)
    
    # print(type(text_complete))
    # print(text_complete[:100])
    
    # extract + classify content 
    engine = ExtractionEngine(llm_config)

    docs = []
    for name, text in texts.items():   
        logger.info("Start extracting info from text:\t%s",
                    name) 
        
        result, info_extract = engine.extract_info_with_retry(text)

        result_dict = result.model_dump()

        extract_res_path = f"{data_processed}/{now}_{name}_response_extract.json"
        fh.save_dict(result_dict, extract_res_path)
        
        docs.append(result)

        logger.info("Result %s:\n%s",
                    name,
                    result_dict)

        settings[f"extract_info_{name}"] = info_extract
        
    # pre-aggregate results from extracted text
    pre_aggregator = AggregationEngine()

    # docs = []
    # for f in file_name:
    #     f_short = f.split(".")[0]
    #     f_path = f"{data_processed}/{now}_{f_short}_llm_response.json"

    #     resp_dict = fh.load_dict(f_path)
    #     docs.append(ExtractedDocument(**resp_dict))

    pre_agg_result = pre_aggregator.aggregate(docs)
    pre_agg_dict = pre_agg_result.model_dump()

    gh.pretty_logging(pre_agg_dict)

    # agg_path = f"{data_processed}/{now}_response_pre_aggregated.json"
    # fh.save_dict(agg_dict, agg_path)
    """
    besseres Matching (Fuzzy / NLP)
    """
 
    # prepare + process LLM input
    llm_input = llm.build_llm_aggregation_input(docs, pre_agg_result)    
    
    llm_aggregation = LLMAggregationEngine(llm_config)
    llm_agg_result, info_agg = llm_aggregation.aggregate_with_retry(llm_input)
    
    gh.pretty_logging(llm_agg_result.model_dump())

    agg_res_path = f"{data_processed}/{now}_response_aggregate.json"
    fh.save_dict(llm_agg_result.model_dump(), agg_res_path)

    settings["aggregation_info"] = info_agg

    settings_path = f"{data_processed}/{now}_settings_llm.json"
    fh.save_dict(settings, settings_path)

    # draw conclusion make a decision = tool.make_decision(structured)
    # decision_engine = DecisionEngine()
    # decision = decision_engine.decide(llm_agg_result, n_docs=len(docs))
    # print(decision.model_dump())

    """
    👉 Report Builder (Markdown + PDF + Streamlit)
    👉 oder LLM Decision Layer (deutlich stärker, 
    aber auch komplexer)
    """
    # return {
    #     "category": category,
    #     "data": structured,
    #     "decision": decision
    # }

if __name__ == "__main__":
    agentic_text_parsing()

# if __name__ == "__main__":
#     file_name = "beyond_DA_hypothesis.pdf"
#     run_exemple(file_name) 

