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
from src.agent.orchestrator import AnalysisOrchestrator

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
@click.option("--config_name", 
              prompt="Name of 'config_file' (no suffix)",
              help='The config_file to use.')
def orchestrated_text_parsing(config_name):  
    
    return run_orchestrated_text_parsing(config_name)

def run_orchestrated_text_parsing(config_name: str):
    # load env variables and config
    gh.load_env_vars()
    # data_raw = os.getenv("DATA_RAW")
    # data_processed = os.getenv("DATA_PROCESSED")
    report_folder = os.getenv("FOLDER_REPORT")
    
    config = fh.get_yaml_config(config_name)
    general_config = config.get("general_args", {})
    # log_name = general_config["name_log"]
    # name_logfile = general_config["name_logfile"]

    llm_config = config.get("llm_settings", {})
    
    # setup logger
    # logger = create_logger(name=log_name, file_name=name_logfile)
    # session.logger = logger

    # extract text from pdf + cleaning
    now = "2026-04-10_11-59-06" 
    # now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session.now = now

    pdf_folder = general_config.get("file_name") or str(general_config.get("folder_name"))
    if pdf_folder is None:
        raise ValueError("In configuration file, 'file_name' or 'folder_name' must not be None.")
    
    orchestrator = AnalysisOrchestrator(
                            extraction=ExtractionEngine,
                            agg_det=AggregationEngine, 
                            agg_llm=LLMAggregationEngine, 
                            decision=LLMDecisionEngine, 
                            reporter=ReportBuilder,
                            config=llm_config
                            )
    md_report = orchestrator.run(pdf_folder)

    report_name = f"{now}_report_llm"
    fh.save_md_file(md_report, report_name, report_folder)



if __name__ == "__main__":
    orchestrated_text_parsing()

# if __name__ == "__main__":
#     file_name = "beyond_DA_hypothesis.pdf"
#     run_exemple(file_name) 

