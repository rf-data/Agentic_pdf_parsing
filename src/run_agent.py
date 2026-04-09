## run_agent.py
# import
import click
import os
from datetime import datetime


from src.agent.extraction import ExtractionEngine
from src.agent.aggregation import AggregationEngine
from src.agent.decision import DecisionEngine
from src.core.session import session
from src.core.logger import create_logger
from src.schema.extraction_schema import ExtractedDocument
import src.tools.text_extraction as extract
import src.utils.general_helper as gh
import src.utils.file_helper as fh
from src.utils.file_helper import get_yaml_config


# ------------------
# MAIN FUNCTION
# ------------------

@click.command()
@click.option("--config_name", prompt="Name of 'config_file' (no suffix)",
              help='The config_file to use.')
def agentic_text_parsing(config_name):  
    
    run_agentic_text_parsing(config_name)

    return

def run_agentic_text_parsing(config_name: str):
    # load env variables and config
    gh.load_env_vars()
    data_raw = os.getenv("DATA_RAW")
    data_processed = os.getenv("DATA_PROCESSED")
    
    config = get_yaml_config(config_name)
    general_config = config.get("general_args", {})
    file_name = general_config["file_name"]
    log_name = general_config["name_log"]
    name_logfile = general_config["name_logfile"]

    llm_config = config.get("llm_settings", {})
    
    # setup logger
    logger = create_logger(name=log_name, file_name=name_logfile)
    session.logger = logger

    # extract text from pdf + cleaning
    # now = "2026-03-31_13-58-36" 
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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

    for name, text in texts.items():   
        logger.info("Start extracting info from text:\t%s",
                    name) 
        
        result, info = engine.extract_info_with_retry(text)

        result_dict = result.model_dump()
        result_path = f"{data_processed}/{now}_{name}_llm_response.json"
        fh.save_dict(result_dict, result_path)

        logger.info("Result %s:\n%s",
                    name,
                    result_dict)

        settings.update(info)
        settings_path = f"{data_processed}/{now}_{name}_llm_settings.json"
        fh.save_dict(settings, settings_path)

    # aggregate results from extracted text
    aggregator = AggregationEngine()

    docs = []
    for f in file_name:
        f_short = f.split(".")[0]
        f_path = f"{data_processed}/{now}_{f_short}_llm_response.json"

        resp_dict = fh.load_dict(f_path)
        docs.append(ExtractedDocument(**resp_dict))

    agg_result = aggregator.aggregate(docs)
    agg_dict = agg_result.model_dump()
    # logger.info("Aggregated reponse:\n%s",
    #             agg_dict)
    gh.pretty_logging(agg_dict)

    agg_path = f"{data_processed}/{now}_response_aggregated.json"
    fh.save_dict(agg_dict, agg_path)
    
    """
    besseres Matching (Fuzzy / NLP)
    LLM-basierte Aggregation (richtig stark)
    Report Builder (Portfolio-ready Output)
    """
 
    # draw conclusion make a decision = tool.make_decision(structured)
    decision_engine = DecisionEngine()
    decision = decision_engine.decide(agg_result, n_docs=len(docs))
    print(decision.model_dump())

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

