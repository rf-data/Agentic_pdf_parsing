## run_text_extraction.py
# import
import click
import os
from pathlib import Path
from datetime import datetime
import pandas as pd


from src.agent.extraction import ExtractionEngine
from src.agent.aggregation_determ import AggregationEngine
from src.agent.aggregation_llm import LLMAggregationEngine
# from src.agent.decision_determ import DecisionEngine
from src.agent.decision_llm import LLMDecisionEngine
from src.agent.report_llm import ReportBuilder

from src.core.memory import session
from src.core.logger import create_logger
# from src.schema.extraction_schema import ExtractedDocument
import src.tools.extraction as extract

import src.utils.general_helper as gh
import src.utils.df_helper as dfh
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
def text_extraction(config_name):  
    # load env variables and config
    gh.load_env_vars()
    config = fh.get_yaml_config(config_name)

    return run_text_extraction(config)


def run_text_extraction(config: dict):
    # load env variables and config
    gh.load_env_vars()
    data_raw = os.getenv("DATA_RAW")
    data_processed = os.getenv("DATA_PROCESSED")
    # report_folder = os.getenv("FOLDER_REPORT")
    
    # config = fh.get_yaml_config(config_name)
    general_config = config.get("general_args", {})
    file_name = general_config["file_name"]
    log_name = general_config["name_log"]
    name_logfile = general_config["name_logfile"]

    preprocess_config = config.get("preprocessing", {})
    llm_config = config.get("llm_settings", {})
    
    # setup logger
    logger = create_logger(name=log_name, file_name=name_logfile)
    session.logger = logger

    # extract text from pdf + cleaning
    # now = "2026-04-10_11-59-06" 
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session.state.now = now

    if isinstance(file_name, str):
        file_name = [file_name]
    
    # page_docs = []
    # chunk_docs = []
    # settings = {
    #         "llm_config": llm_config
    #         }
    
    for name in file_name:
        logger.info("Start extracting text from file:\t%s",
                    name)
        # name_short = name.split(".")[0]

        f_path = f"{data_raw}/{name}"
        extract_result = extract.extract_per_page(
                                                f_path, 
                                                preprocess_config,
                                                # save_df=True
                                                )
        # text_spacy = 

        # settings.update(info)
        # result = {
        #     "document_name": name_short,    
        #     "pages": extract_result    
        #     }

        # page_docs.append(extract_result["pages"])         # = List[dict]
        # chunk_docs.append(extract_result["chunks"])
        # # text[name_short] = str(cleaned_text)

        # df_

        df_pages = pd.DataFrame(extract_result["pages"])
        df_chunks = pd.DataFrame(extract_result["chunks"])

        logger.info("Head 'pages_df':\n%s", df_pages.head())
        logger.info("Head 'chunks_df':\n%s", df_chunks.head())

        logger.info("dtypes in 'pages_df'")
        for col in df_pages.columns:
            logger.info("Col '%s':\t%s",
                        col, 
                        df_pages[col].map(type).unique())

        logger.info("dtypes in 'df_chunks'")
        for col in df_chunks.columns:
            logger.info("Col '%s':\t%s",
                        col, 
                        df_chunks[col].map(type).unique())
            
        timestamp = session.state.now
        f_name = Path(f_path).stem   # name.split(".")[0]
        data_processed = os.getenv("DATA_PROCESSED")
        
        chunk_folder = f"{data_processed}/chunk_df"
        chunk_file = f"{timestamp}_{f_name}_chunk_df"
        dfh.save_df_to_parquet(
                            df=df_chunks, 
                            f_name=chunk_file,
                            folder=chunk_folder, 
                            # chunked=True
                            )

        page_folder = f"{data_processed}/page_df"
        page_file = f"{timestamp}_{f_name}_page_df"
        dfh.save_df_to_parquet(
                            df=df_pages, 
                            f_name=page_file,
                            folder=page_folder, 
                            # chunked=True
                            )
        
        words = extract_result.get("words", {})
        if len(words) > 0:
            df_words = pd.DataFrame(words)
            logger.info("Head 'df_words':\n%s", df_words.head())
            logger.info("dtypes in 'df_words'")
        
            for col in df_words.columns:
                logger.info("Col '%s':\t%s",
                            col, 
                            df_words[col].map(type).unique())
                
            word_folder = f"{data_processed}/word_df"
            word_file = f"{timestamp}_{f_name}_word_df"
            dfh.save_df_to_parquet(
                                df=df_words, 
                                f_name=word_file,
                                folder=word_folder, 
                                # chunked=True
                                )




    # result_path = f"{data_processed}/{now}_texts_raw.json"
    # fh.save_dict(docs, result_path)
        
    return 

if __name__ == "__main__":
    text_extraction()
