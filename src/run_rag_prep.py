## run_rag_preparation
# imports
import click
from typing import List
import os
from pathlib import Path
import pandas as pd

from src.core.memory import session
from src.core.logger import create_logger

import src.utils.general_helper as gh
import src.utils.file_helper as fh
import src.utils.df_helper as dfh

from src.tools.cleaning import chunk_by_sentences, clean_text, remove_noise

# ------------------
# MAIN FUNCTION
# ------------------
@click.command()
@click.option("--config_name", 
              prompt="Name of 'config_file' (no suffix)",
              help='The config_file to use.')
def prepare_rag(config_name):  
    
    return run_prepare_rag(config_name)

def run_prepare_rag(config_name):
    # load env variables and config
    gh.load_env_vars()
    data_processed = os.getenv("DATA_PROCESSED")

    config = fh.get_yaml_config(config_name)
    general_config = config.get("general_args", {})
    file_name = general_config["file_name"]
    log_name = general_config["name_log"]
    name_logfile = general_config["name_logfile"]
    timestamp = general_config["timestamp"]

    session.now = timestamp

    prep_config = config.get("preparation", {})

    # setup logger
    logger = create_logger(name=log_name, file_name=name_logfile)
    session.logger = logger

    # load text_df
    if isinstance(file_name, str):
        file_name = [file_name]
    
    df_paths = []
    for name in file_name:
        df_path = 
        df_paths.append(f"{data_processed}/{timestamp}_{name}_df_chunks")
        
    dict_path = f"{data_processed}/{file_name}"
    text_dicts = fh.load_dict(dict_path)
    print("[DEBUG] text_dicts")
    print(type(text_dicts))
    print(len(text_dicts))
    print(text_dicts[0].keys())

    text_data, chunk_data = prepare_rag_text(
                                        text_dicts, 
                                        prep_config,
                                        as_df=True,
                                        # save_folder=data_processed
                                        )

    logger.info("Text_data")
    logger.info("Head:\n%s\n", text_data.head())
    logger.info("Chunk_data")
    logger.info("Head:\n%s\n", chunk_data.head())
    logger.info("Description of 'n_tokens';\n%s\n",
                chunk_data["n_tokens"].describe(percentiles=[]))

    return 


def prepare_rag_text(texts: List[dict], 
                     prep_config: dict,
                     as_df: bool=False,
                     save_folder: str | Path = None):
    # setup logger
    logger = session.logger

    chunking = prep_config["chunking"]
    overlap = prep_config["overlap"]
    pattern = prep_config["noise_patterns"]

    chunks_prep = {}
    texts_prep = {}
    doc_name = ""
    for doc in texts:
        doc_name = doc["document_name"]
        pages = doc["pages"]

        logger.info("Start preparing file '%s'",
                    doc_name)

        chunks_prep[doc_name] = []
        texts_prep[doc_name] = []

        for page_info in pages:
            n_page = page_info["page"]
            text = page_info["text"]

            if isinstance(text, list):
                text = text[0] 

            logger.info("File '%s' (page = %s) -- info on 'text'",
                        doc_name,
                        n_page)
            logger.info("Type: %s", type(text))
            logger.info("Length: %s", len(text))
            logger.info("First 50 chars: %s\n", text[:50])
                        
            if len(text) < 50:
                continue
                            
            text_clean = clean_text(text)
            text_noise = remove_noise(text_clean, pattern)
            # text_low = text_clean.lower()

            # print("[DEBUG] 'text_clean'")
            # print(type(text_clean))
            # print(len(text_clean))
            # print(text_clean[0])
                    
            texts_prep[doc_name].append({
                            "document_name": doc_name,
                            "page": n_page,
                            "text": text_noise,
                            "text_lower": text_noise.lower(),
                        })
                        
            if chunking:
                text_chunks = chunk_by_sentences(
                                    text_noise, 
                                    prep_config
                                    )
                            
                for chunk in text_chunks:
                    chunk["document_name"] = doc_name
                    chunk["page"] = n_page
                    id = chunk["chunk_id"]
                    chunk["chunk_id"] = f"p{n_page}_c{id}"
                    
                    chunks_prep[doc_name].append(chunk)

    if as_df:
        texts_flat = [item for sublist in texts_prep.values() 
                      for item in sublist]
        texts_prep = pd.DataFrame(texts_flat)

        chunks_flat = [item for sublist in chunks_prep.values() 
                      for item in sublist]
        chunks_prep = pd.DataFrame(chunks_flat)

    if save_folder:
        # folder_path = Path(data_processed)
        timestamp = session.now
        chunk_file = f"{timestamp}_chunks"
        text_file = f"{timestamp}_texts"

        if as_df: 
            dfh.save_df_to_parquet(
                        df=chunks_prep, 
                        f_name=chunk_file, 
                        folder= save_folder,
                        chunked=True
                        )
    
            dfh.save_df_to_parquet(
                            df=texts_prep, 
                            f_name=text_file, 
                            folder= save_folder,
                            chunked=True
                            )
        
        else: 
            text_path = f"{save_folder}/{text_file}.json"
            fh.save_dict(texts_prep, text_path)

            chunk_path = f"{save_folder}/{chunk_file}.json"
            fh.save_dict(chunks_prep, chunk_path)     

    return texts_prep, chunks_prep



if __name__ == "__main__":
    prepare_rag()


"""

"""