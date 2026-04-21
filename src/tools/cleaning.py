## text_cleaning.py
# import
import re
from collections import Counter

from src.utils.spacy_helper import load_spacy_model


# WHITELIST = [
#         "dopamine", "serotonin", "schizophrenia", 
#         "psychotic", "symptom", "drug", 
#         "receptor", "glutamate", "agonist", 
#         "antagonist", "pathway", "psychosis", 
#         "hypothesis", "hypotheses", "neural", 
#         "signaling", "cortex", "pharmacologic"
#              ]

# -----------------------
# FOOTER / HEADER REMOVAL
# -----------------------

def detect_repeated_lines(pages: dict[str, str], 
                          min_count: int=3):
    line_counts = Counter()

    for page in pages:
        # text = page.extract_text()
        text = page["text_raw"] # .extract_text(x_tolerance=2, y_tolerance=2)  # (layout=True)       # x_tolerance=2, y_tolerance=2

        if not text:
            continue

        lines = text.split("\n")
        
        for line in lines:
            if line:       # len(line) > 7
                line_counts[line.strip()] += 1

    return {
        line for line, count in line_counts.items()
        if count > min_count   # threshold anpassen
    }


# def remove_repeated_lines(text, lines):

#     for l in lines:
#         text = re.sub(l.strip(), '', text, flags=re.IGNORECASE)

#     return text


def remove_noise_pattern(text, pattern):
    
    for p in pattern:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    
    return re.sub(r"\n{2,}", "\n", text).strip()


def header_footer_cutoff(text):
    lines = text.split("\n")
    core = lines[2:-2]  # erste + letzte 2 Zeilen raus

    return core
# ------------------
# TEXT CLEANING
# ------------------



# def extract_words_pymupdf(path):
#     doc = fitz.open(path)
#     pages = []

#     for i, page in enumerate(doc):
#         words = page.get_text("words")  
#         # (x0, y0, x1, y1, "word", block_no, line_no, word_no)

#         words_sorted = sorted(words, key=lambda w: (w[1], w[0]))

#         text = " ".join([w[4] for w in words_sorted])

#         pages.append({
#             "page": i,
#             "text": text
#         })

#     return pages


# def extract_blocks(path):
#     doc = fitz.open(path)
#     pages = []

#     for i, page in enumerate(doc):
#         blocks = page.get_text("blocks")

#         cleaned_blocks = []

#         for b in blocks:
#             x0, y0, x1, y1, text, *_ = b

#             # Beispiel: Header/Footer entfernen
#             if y0 < 50 or y1 > page.rect.height - 50:
#                 continue

#             cleaned_blocks.append(text)

#         pages.append({
#             "page": i,
#             "text": "\n".join(cleaned_blocks)
#         })

#     return pages


# def split_sections(text: str):
#     print(f"START 'split_sections'")

#     sections = re.split(r'\n(?=[A-Z][A-Za-z ]{5,})', text)
#     return sections


def clean_text(text: str):
    text = text.replace("\n", " ")      # .replace("  ", " ")
    text = " ".join(text.split())

    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

    return text.strip()


# def text_repair_spacy(self, text):
#         config = self.preprocess_config
#         spacy_lang = config["spacy_language"]

#         nlp = load_spacy_model(spacy_lang)
#         doc = nlp(text)

#         tokens = [token.text for token in doc]

#         sentences = [sent.text for sent in doc.sents]

#         return {
#             "tokens": tokens,
#             "sentences": sentences
#             }

# def text_repair_tokenizer():
#     # lazy import
#     from transformers import AutoTokenizer

#     tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

#     tokens = tokenizer.tokenize(text)
    
#     return tokens

# tokens = tokenizer(text)["input_ids"]

    # chunks = [
    #     tokens[i:i+256]
    #     for i in range(0, len(tokens), 200)
    # ]


# def text_repair_LLM():
#     # lazy import (openAI)
    
#     return 
# def normalize_pdf_artifacts(text: str):


#     return 


def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i+chunk_size]

        text = " ".join(chunk)

        chunks.append({
            "chunk_id": i,
            "text_chunk": text,
            "n_tokens": len(text) 
            })
    
    return chunks


def chunk_by_sentences(text, prep_config):
    max_tokens = prep_config["max_tokens"]
    spacy_lang = prep_config["spacy_language"] 

    nlp = load_spacy_model(spacy_lang)
    doc = nlp(text)

    chunks = []
    current = []
    current_len = 0
    chunk_id = 1

    for sent in doc.sents:
        tokens = len(sent.text.split())

        if current_len + tokens > max_tokens:
            text = " ".join(current)
            chunks.append({
                    "chunk_id": chunk_id,
                    "text": text, 
                    "n_tokens": len(text)
            })
           
            current = []
            current_len = 0
            chunk_id += 1

        current.append(sent.text)
        current_len += tokens

    if current:
        text_curr = " ".join(current)
        chunks.append({
            "chunk_id": chunk_id,
            "text_chunk": text_curr,
            "n_tokens": len(text_curr) 
            })

    return chunks