## run_agent.py
# import
import click
import os
from pathlib import Path
from datetime import datetime


from src.agent.extraction import ExtractionEngine
from src.agent.aggregation_determ import AggregationEngine
from src.agent.aggregation_llm import LLMAggregationEngine
# from src.agent.decision_determ import DecisionEngine
from src.agent.decision_llm import LLMDecisionEngine
from src.agent.report_llm import ReportBuilder

from src.core.session import session
from src.core.logger import create_logger
# from src.schema.extraction_schema import ExtractedDocument
import src.tools.extraction as extract

import src.utils.general_helper as gh
import src.utils.llm_helper as llm
import src.utils.file_helper as fh
# import get_yaml_config


# ------------------
# MAIN FUNCTION
# ------------------

@click.command()
@click.option("--config_name", 
              prompt="Name of 'config_file' (no suffix)",
              help='The config_file to use.')
def agentic_text_parsing(config_name):  
    
    return run_agentic_text_parsing(config_name)

def run_agentic_text_parsing(config_name: str):
    # load env variables and config
    gh.load_env_vars()
    data_raw = os.getenv("DATA_RAW")
    data_processed = os.getenv("DATA_PROCESSED")
    report_folder = os.getenv("FOLDER_REPORT")
    
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
    # now = "2026-04-10_11-59-06" 
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session.now = now

    if isinstance(file_name, str):
        file_name = [file_name]
    
    docs = []
    settings = {
            "llm_config": llm_config
            }
    
    for name in file_name:
        logger.info("Start extracting text from file:\t%s",
                    name)
        name_short = name.split(".")[0]

        f_path = f"{data_raw}/{name}"
        extract_result, info = extract.extract_text_per_page(f_path, save=False)
        # text_spacy = 

        settings.update(info)
        result = {
            "document_name": name_short,    
            "pages": extract_result    
            }

        docs.append(result)
        # text[name_short] = str(cleaned_text)

    result_path = f"{data_processed}/{now}_texts_raw.json"
    fh.save_dict(docs, result_path)
        
    # # extract + classify content 
    # engine = ExtractionEngine(llm_config)

    # llm_result = {
    #         "doc_name": "",

    # }
    # for (doc_name, ext_results) in docs:   
    #     logger.info("Start extracting info from text:\t%s",
    #                 doc_name) 
        
    #     llm_result[""]
    #     for page, text in ext_results.items():

    #         if isinstance(text, str):
    #             result, info_extract = engine.extract_info_with_retry(text)

    #             result_dict = result.model_dump()
                
    #         elif isinstance(text, dict) and "chunk_id" in text.keys():
                
    #             result_dict = {}
    #             for chunk_id, chunk in text.items():
    #                 result, info_extract = engine.extract_info_with_retry(chunk)

    #                 result_dict[chunk_id] = result.modle_dump()

    #     # txttxt_result = {
    #     #         "page": page,
    #     #         "text":
    #     # }

    #     extract_res_path = f"{data_processed}/{now}_{name}_response_extract.json"
    #     fh.save_dict(result_dict, extract_res_path)
        
    #     extract.append(result)

    #     logger.info("Result %s:\n%s",
    #                 name,
    #                 result_dict)

    #     settings[f"extract_info_{name}"] = info_extract
        
    # # pre-aggregate results from extracted text
    # pre_aggregator = AggregationEngine()
    # pre_agg_result = pre_aggregator.aggregate(extract)
    # pre_agg_dict = pre_agg_result.model_dump()

    # gh.pretty_logging(pre_agg_dict)
    # # agg_path = f"{data_processed}/{now}_response_pre_aggregated.json"
    # # fh.save_dict(agg_dict, agg_path)
  
    # # prepare + process LLM input
    # llm_input = llm.build_llm_aggregation_input(docs, pre_agg_result)    
    
    # llm_aggregation = LLMAggregationEngine(llm_config)
    # agg_result, info_agg = llm_aggregation.aggregate_with_retry(llm_input)
    # settings["aggregation_info"] = info_agg

    # agg_result_dict = agg_result.model_dump()
    # gh.pretty_logging(agg_result_dict)

    # agg_res_path = Path(f"{data_processed}/{now}_response_aggregate.json")
    # fh.save_dict(agg_result_dict, agg_res_path)

    # # dict_path = f"{data_processed}/{now}_response_aggregate.json"
    # # agg_result_dict = fh.load_dict(dict_path)
    # # draw conclusion make a decision = tool.make_decision(structured)
    # decision_engine = LLMDecisionEngine(llm_config)

    # decision, info_decide = decision_engine.decide(agg_result)
    # decision_dict = decision.model_dump()
    # gh.pretty_logging(decision_dict) 

    # settings["aggregation_info"] = info_decide
    # settings_path = Path(f"{data_processed}/{now}_settings_llm_v2.json")
    # fh.save_dict(settings, settings_path)

    # rep_builder = ReportBuilder(agg_result, decision)
    # md_report = rep_builder.build_md_report()

    # report_name = f"{now}_report_llm"
    # fh.save_md_file(md_report, report_name, report_folder)
    # # return {
    # #     "category": category,
    # #     "data": structured,
    # #     "decision": decision
    # # }



if __name__ == "__main__":
    agentic_text_parsing()

# if __name__ == "__main__":
#     file_name = "beyond_DA_hypothesis.pdf"
#     run_exemple(file_name) 

