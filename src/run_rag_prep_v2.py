## run_rag_preparation
# imports
import click
from typing import List
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

from src.core.memory import session
from src.core.logger import create_logger

import src.utils.general_helper as gh
import src.utils.file_helper as fh
import src.utils.df_helper as dfh

# from src.tools.cleaning import chunk_by_sentences, clean_text, remove_noise

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
    # file_name = general_config["file_name"]
    log_name = general_config["name_log"]
    name_logfile = general_config["name_logfile"]
    timestamp = general_config["timestamp"]

    session.state.now = timestamp

    # prep_config = config.get("preparation", {})

    # setup logger
    logger = create_logger(name=log_name, file_name=name_logfile)
    session.logger = logger

    # load text_dict
    # 2026-04-18_17-38-11_beyond_DA_hypothesis_page_df.parquet
    folders = [
            f"{data_processed}/chunk_df", 
            f"{data_processed}/page_df"
            ]
    dfs_list = load_check_df(folders, timestamp, "parquet")

    df_to_merge = []
    for df_dict in dfs_list:
        # for df_name, df in df_dict.items():
        df_to_merge.append([df_dict.values()]) #    = [df for df in df_dict.values()]

    df_merge = pd.concat(df_to_merge, ignore_index=True)

    logger.info("\n%s DF_MERGED %s\n",
                        "=" * 15,
                        "=" * 15,)
                        # \nName:\t%s", df_name)
    logger.info("\nShape:\t%s\n", 
                        df_merge.shape)
    logger.info("\nHead:\n%s\n", 
                        df_merge.head())
    logger.info("\nDescription:\n%s\n", 
                        df_merge.describe(percentiles=percents))
    logger.info("\nDuplicates:\n%s\n", 
                        df_merge.duplicated().sum())
    """
    1️⃣ Daten bereinigen
    df = pd.concat(all_chunk_dfs, ignore_index=True)

    df = df.drop_duplicates(subset=["chunk_id"])
    df = df[df["text_chunk"].notna()]

    2️⃣ Chunk Size fixen (wichtig!)

    Falls du neu chunkst:
    target_tokens = 300
    Zielgröße
    200 – 500 Tokens
    (max ~800)

    Chunk-Größe → kritisch für RAG

    Du hast:
    n_tokens:
    mean ~2500–4000
    max ~6000

👉 Das ist zu groß.

    3️⃣ Minimal-RAG Setup
    df["embedding_input"] = df["text_chunk"]

    4️⃣ Embeddings bauen
    (z. B. OpenAI / sentence-transformers)

    df["text_for_embedding"] = df["text_chunk"]

    👉 später evtl.:
    cleaned
    stopwords entfernt
    normalisiert

    Kontext-Feld für Ausgabe
    df["text_for_llm"] = df["text_chunk"]

    5️⃣ Retrieval testen
    Top-k:

    k = 3–5
    """
    return 

def load_check_df(folder: str | Path| List[str], 
                  timestamp, 
                  f_type="parquet") -> List[dict[str, pd.DataFrame]]:
    # setup logger
    logger = session.logger

    if isinstance(folder, (str, Path)):
        folder = [folder]

    dfs = []
    for f in folder:    
        # folder_pages = f"{folder}/page_df"
        # f_patholder_chunks = f"{folder}/chunk_df"

        # REMOVE DUPLICATES
        # df = df.drop_duplicates(subset=["chunk_id"])

        df_dict = dfh.load_files_from_folder(
                                            folder=f, 
                                            timestamp=timestamp,
                                            # suffix="", 
                                            f_type=f_type
                                            )

        dfs.append(df_dict)

        percents = [.01, .05, .1, .25, .5, .75, .9, .95, .99]
        # for name, df_dict in [("pages_df", page_dfs),
        #              ("chunks_df", chunk_dfs)]: 
        #   # , "\n"), 
        # logger.info("%s\n--- %s --- %s  ---\n",
        #             "=" * 50, 
        #             name.upper(),
        #             datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #             )
        # now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        for df_name, df in df_dict.items():
            logger.info("\n%s %s %s\n",
                        "=" * 15, 
                        df_name.upper(),
                        "=" * 15,)
                        # \nName:\t%s", df_name)
            logger.info("\nShape:\t%s\n", 
                        df.shape)
            logger.info("\nHead:\n%s\n", 
                        df.head())
            logger.info("\nDescription:\n%s\n", 
                        df.describe(percentiles=percents))
            logger.info("\nDuplicates:\n%s\n", 
                        df.duplicated().sum())
        
        logger.info("%s\n", "=" * 50) 

    # [f for f in Path(folder_chunks).iterdir() if f.stem.startswith(timestamp)]
    # page_dfs = dfh.load_files_from_folder(
    #                                     folder_pages, 
    #                                     timestamp=timestamp,
    #                                     # suffix= "", 
    #                                     f_type="parquet"
    #                                     )
    # [f for f in Path(folder_pages).iterdir() if f.stem.startswith(timestamp)]

    return dfs
    
    # print(len(text_dicts))
    # print(text_dicts[0].keys())


    # text_data, chunk_data = prepare_rag_text(
    #                                     text_dicts, 
    #                                     prep_config,
    #                                     as_df=True,
    #                                     # save_folder=data_processed
    #                                     )

    # logger.info("Text_data")
    # logger.info("Head:\n%s\n", text_data.head())
    # logger.info("Chunk_data")
    # logger.info("Head:\n%s\n", chunk_data.head())
    # logger.info("Description of 'n_tokens';\n%s\n",
    #             chunk_data["n_tokens"].describe(percentiles=[]))

    # return 


# def prepare_rag_text(texts: List[dict], 
#                      prep_config: dict,
#                      as_df: bool=False,
#                      save_folder: str | Path = None):
#     # setup logger
#     logger = session.logger


#     chunks_prep = {}
#     texts_prep = {}
    
#     for doc in texts:
#         doc_name = doc["document_name"]
#         pages = doc["pages"]

#         logger.info("Start preparing file '%s'",
#                     doc_name)

#         chunks_prep[doc_name] = []
#         texts_prep[doc_name] = []

#         for page_info in pages:
#             n_page = page_info["page"]
#             text = page_info["text"]

#             if isinstance(text, list):
#                 text = text[0] 
                
#         extract_dict = extract_per_page(
#                                     f_path="" ,
#                                     prep_config,
#                                     save=True
#                                     )
        
#     return 



if __name__ == "__main__":
    prepare_rag()

