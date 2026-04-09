## text_extraction.py
# import
import pdfplumber
import re
# import gc
from typing import List
from datetime import datetime
import os
from pathlib import Path

# from wordfreq import zipf_frequency

import src.utils.file_helper as fh
from src.core.text_cleaner import TextCleaner
from src.core.session import session

WHITELIST = [
        "dopamine", "serotonin", "schizophrenia", 
        "psychotic", "symptom", "drug", 
        "receptor", "glutamate", "agonist", 
        "antagonist", "pathway", "psychosis", 
        "hypothesis", "hypotheses", "neural", 
        "signaling", "cortex", "pharmacologic"
             ]

# ------------------
# TEXT EXTRACTION
# ------------------
def extract_text(file_path: str) -> str:
    texts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text)

    return "\n".join(texts)


def extract_text_per_page(f_path:str, save=False) -> List:
    f_name = Path(f_path).name.split(".")[0]
    cleaner = TextCleaner(whitelist=WHITELIST, 
                          f_name=f_name,
                          debug=True)
    
    pages = []

    with pdfplumber.open(f_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i > 0: 
                print()
            
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"=== PROCESSING PAGE {i} ({now}) ===")
            
            text = page.extract_text()
            text_clean = cleaner.clean(text)

            text_split = cleaner.split(text_clean)
            text_blocks = split_sections(text_split)

            pages.append(text_blocks)

    info = {
        "white_list": WHITELIST
        }

    if save:
        timestamp = session.now
        file_name = Path(f_path).name.split(".")[0]
        data_processed = os.getenv("DATA_PROCESSED")

        save_path = f"{data_processed}/{timestamp}_{file_name}_extracted.json"

        fh.save_dict(pages, save_path)

    return pages, info


# ------------------
# TEXT CLEANING
# ------------------

def split_sections(text: str):
    print(f"START 'split_sections'")

    sections = re.split(r'\n(?=[A-Z][A-Za-z ]{5,})', text)
    return sections


# def text_cleaning(text: str):
#     text_clean = clean_text(text)
#     text_cleaned = remove_noise(text_clean)

#     text_white_fixed = apply_whitelist_split(text_cleaned)
#     text_fixed = fix_split_text(text_white_fixed)

#     return text_fixed


# def fix_split_text(text):
#     words = text.split()
#     words_corrected = [split_word(w) for w in words]
    
#     return " ".join(words_corrected)

    # return text_cleaned


# def split_with_whitelist(word: str, whitelist: list):
#     for w in whitelist:
#         idx = word.lower().find(w.lower())
#         if idx > 0:
#             left = word[:idx]
#             right = word[idx:]
#             return left + " " + right

#     return word


# def apply_whitelist_split(text: str):
#     words = text.split()
#     new_words = [split_with_whitelist(w, WHITELIST) for w in words]
#     return " ".join(new_words)


# def clean_text(text: str) -> str:
#     # Fix missing white spaces after dot, colon and semicolon
#     text = re.sub(r'([,;:])(?=\S)', r'\1', text)

#     # 
#     text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
#     text = re.sub(r'\.(?=[A-Z])', '. ', text)
    
#     # Fix 'merged words' / missing white spaces
#     text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
#     # multiple white spaces
#     text = re.sub(r'\s+', ' ', text)

#     return text.strip()


# def split_word(word):
#     # sehr einfache Heuristik
#     for i in range(3, len(word)-3):
#         left = word[:i]
#         right = word[i:]
        
#         if zipf_frequency(left, "en") > 3 and zipf_frequency(right, "en") > 3:
#             return left + " " + right

#     return word
