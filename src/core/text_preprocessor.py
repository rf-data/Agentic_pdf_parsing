## text_cleaner.py
# import
import re
# import subprocess
# import gc
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

# from src.core.logging import create_logger
from src.utils.spacy_helper import load_spacy_model

try:
    from wordfreq import zipf_frequency
    WORD_FREQ_AVAILABLE = True
except ImportError:
    WORD_FREQ_AVAILABLE = False


@dataclass
class CleaningStats:
    total_words: int = 0
    split_words: int = 0
    whitelist_splits: int = 0

@dataclass
class TextPreprocessor:
    
    # def __init__(self, f_name, preprocess_config, ):
    f_name: str = ""
    preprocess_config: Dict = field(default_factory=dict)
    whitelist: Optional[List[str]] = field(default_factory=list)
    noise_pattern: Optional[List[str]] = field(default_factory=list)
    whitelist_lower: Optional[List[str]] = field(default_factory=list)

    debug: bool = False
    stats: CleaningStats = field(default_factory=CleaningStats)

        
    # -------------------------
    # Public API
    # -------------------------
    def clean(self, text: str,
              repeated_lines: set[str]) -> str:
        text = self._basic_cleanup(text)
        # text = self._fix_case_boundaries(text)
        text = self._remove_noise(text)
        text = self._remove_repetition_noise(text, 
                                            repeated_lines)

        if self.debug:
            self._print_stats()

        return text


    def group_words(self, words: List[dict[str, Any]], y_tol):
        words_sorted = sorted(words, 
                           key=lambda w: (
                                        round(w["y0"], 1),
                                        w["x0"]
                                        ))
        lines = []
        current_line = []

        for word in words_sorted:
            if not current_line:
                current_line.append(word)
                continue

            if abs(word["y0"] - current_line[-1]["y0"]) < y_tol:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]

        if current_line:
            lines.append(current_line)

        return lines

    """
    words_records.append({
                    "file_name": f_name,
                    "page": i,
                    "block": k,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "text_raw": text,
                    })
    """

    def lines_to_text(self, lines: List[dict[str, Any]]):

        text_lines = []
        for l in lines:
            sorted_line = sorted(l, key=lambda w: w["x0"])
            text = "".join(w["text_raw"] for w in sorted_line)

            y0_min = min(w["y0"] for w in l)
            y1_max = max(w["y1"] for w in l)

            text_lines.append({
                        "text": text,
                        "line_start": y0_min, 
                        "line_end": y1_max
                        })

        return text_lines

    def group_text(self, text_lines: List[dict[str, Any]], y_gap_tol):
        blocks = []
        current_block = []
        
        for line in text_lines:
            if not current_block:
                current_block.append(line)
                continue
        
            prev = current_block[-1]
            gap = line["line_start"] - prev["line_end"]
            if gap < y_gap_tol:
                current_block.append(line)
            else:
                blocks.append(current_block)
                current_block = [line]

        if current_block:
            blocks.append(current_block)

        return blocks 
    

    def blocks_to_text(self, blocks):
        block_texts = []

        for block in blocks:
            text = " ".join(line["text"] for line in block)

            block_texts.append(text)

        return block_texts


    def layout_aware_preparation(self, words: List[dict[str, Any]]):
        y_tol = self.preprocess_config["y_tolerance"] 
        y_gap_tol = self.preprocess_config["y_gap_tolerance"] 

        lines = self.group_words(words, y_tol)
        text_lines = self.lines_to_text(lines)
        blocks = self.group_text(text_lines, y_gap_tol)
        block_texts = self.blocks_to_text(blocks)

        return block_texts


    def semantic_chunking(self, text):
        spacy_lang = self.preprocess_config["spacy_language"]  
        nlp = load_spacy_model(spacy_lang) 

        max_words = self.preprocess_config["max_words"]
        overlap = self.preprocess_config["overlap"]
        min_words = self.preprocess_config["min_words_chunk"]

        # nlp = session.spacy_obj
        doc = nlp(text)
        text_dict = self._split_by_spacy(doc)
        sentences = text_dict["sentences"]

        current = []
        current_len = 0
        chunks = []
        chunk_id = 1

        for sent in sentences:
            sent_len = len(sent.split())

            if current and current_len + sent_len > max_words:
                chunk_text = " ".join(current)
                n_words = len([token for token in nlp(chunk_text)])

                if n_words >= min_words:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text_chunk": chunk_text, 
                        "n_chars": len(chunk_text),
                        "n_words": n_words
                        })

                prev = current.copy()
                chunk_id += 1

                if overlap > 0:
                    current = prev[-overlap:]
                    current_len = sum(len(s.split()) for s 
                                      in current) 

                else: 
                    current = []
                    current_len = 0
           
            current.append(sent)
            current_len += sent_len

        if current and n_words >= min_words:
            chunk_text = " ".join(current)
            n_words = len([token for token in nlp(chunk_text)])

            chunks.append({
                "chunk_id": chunk_id,
                "text_chunk": chunk_text,
                "n_chars": len(chunk_text),
                "n_words": n_words
                })  

        return chunks   # , text_dict
    
    # def clean_v2(self, text):
    #     text = self._fix_joined_words_v2(text)
    #     text = self._basic_cleanup(text)
    #     text = self._remove_noise(text)
    #     # text = self._fix_joined_words(text)
    #     # text = self._apply_whitelist_split(text)
    #     text = self._final_cleanup(text)

    #     return text

    # def split(self, text):
    #     text = self._fix_joined_words(text)
    #     text = self._apply_whitelist_split(text)
    #     text = self._final_cleanup(text)
        
    #     if self.debug:
    #         self._print_stats()

    #     return text
    

    # def normalize_text(text: str):


    # def chunk_by_spacy(self, text):
    #     config = self.preprocess_config
    #     max_tokens = config["max_tokens"]
    #     spacy_lang = config["spacy_language"]

    #     nlp = load_spacy_model(spacy_lang)

    #     if isinstance(text, str):
    #         text = [text]

    #     tokens = []
    #     sent_from_token = []
    #     sentences = []
    #     for t in text:    
    #         doc = nlp(t)

    #         toks = [token.text for token in doc]
    #         tokens += toks
    #         sent_from_token += "".join(toks)
            
    #         sentences += self._chunk_by_sentences(doc, max_tokens)


    #     return {
    #         "tokens": tokens,
    #         "sentences": sentences
    #         }
  
    # -------------------------
    # Steps
    # -------------------------
    def _basic_cleanup(self, text: str) -> str:
        print(f"START 'basic_cleanup'")

        text = text.replace("\n", "")

        # Fix missing white spaces after comma, 
        # colon and semicolon
        text = re.sub(r'([.,;:/])(^\s)', r'\1 \2', text)

        # 
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        
        # multiple white spaces
        text = re.sub(r'\s+', ' ', text)

        # separate letters from digits
        # text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # text = re.sub(r'([a-z])([A-Z])', r'\1\. \2', text)

        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
        
        # text = text.replace("\n", " ")      # .replace("  ", " ")
        # text = " ".join(text.split())
        # text = re.sub(r'(?<=[\.\!\?])\s+', '\n', text)

        return text.strip()


    def _sentence_repair(self, text):
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)
        return text


    def _remove_repetition_noise(
                            self, 
                            text:str, 
                            repeated_lines: set[str]
                            )-> str:

        lines = [ln for ln in text.split("\n") 
                 if ln.strip() not in repeated_lines]
    
        return "\n".join(lines).strip()


    def _remove_noise(self, text):

        if not self.noise_pattern:
            self.noise_pattern = self.preprocess_config["noise_pattern"]

        print(f"START 'remove_noise'")

        # DOI, URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r"(doi:|©|journal|volume|\(\d{4}\))", '', text)
        
        # page numbers 
        text = re.sub(r'[P|p]age \d+ [\/|of] \d+', '', text)
        # text = re.sub(r)
        
        # remove section 'References'
        text = re.split(r'References:', text)[0]

        # remove patterns
        for p in self.noise_pattern:
            text = re.sub(fr'{p}', '', text, flags=re.IGNORECASE)
        
        return re.sub(r"\n{2,}", "\n", text).strip()


    def _final_cleanup(self, text: str) -> str:
        print(f"START 'final_cleanup'")

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*([.,;])\s*', r'\1 ', text)
        return text.strip()

    # -------------------------
    # Chunking
    # -------------------------

    def _split_by_spacy(self, doc):

        sentences = [sent.text.strip() for sent in doc.sents 
                     if sent.text.strip()]

        tokens = [token.text for token in doc]

        return {
            "tokens": tokens,
            "sentences": sentences
            }
    

    def _filter_chunks(self, chunks: Dict, min_words: int):


        return chunks_filt, chunks_short
    
    # -------------------------
    # Debugging
    # -------------------------
    def _print_stats(self):
        from src.core.memory import session
        logger = session.logger

        logger.info("""
        --- TextCleaner Stats (%s)---)
        Total words processed: %s
        Word splits (freq):    %s                    
        Whitelist splits:      %s  
        ------------------------                  
        """,
        self.f_name,
        self.stats.total_words, 
        self.stats.split_words,
        self.stats.whitelist_splits
        )

#         print(f"""
# --- TextCleaner Stats ({self.f_name}) ---
# Total words processed: {self.stats.total_words}
# Word splits (freq):    {self.stats.split_words}                    
# Whitelist splits:      {self.stats.whitelist_splits}
# ------------------------                  
# """)
        
    # def _fix_joined_words(self, text: str) -> str:
    #     print(f"START 'fix_joined_words'")

    #     words = text.split()
    #     new_words = []

    #     k = 0
    #     for word in words:
    #         self.stats.total_words += 1
            
    #         split_word = self._smart_split(word)

    #         if split_word != word:
    #             self.stats.split_words += 1

    #             if k <= 5:
    #                 print("Word conversions:\n", word, "→", split_word)
    #                 k += 1

    #         new_words.append(split_word)

    #     return " ".join(new_words)
    

    # def _fix_joined_words_v2(self, text: str):
    #     text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    #     text = re.sub(r"([a-z])(\d)", r"\1 \2", text)
    #     text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)
        
    #     return text

    # def _smart_split(self, word: str) -> str:
    #     if not WORD_FREQ_AVAILABLE or len(word) < 3:
    #         return word

    #     for i in range(3, len(word) - 3):
    #         left = word[:i]
    #         right = word[i:]

    #         if (
    #             zipf_frequency(left, "en") >= 3          # 3
    #             and zipf_frequency(right, "en") >= 3     # 3
    #         ):
    #             return f"{left} {right}"

    #     return word


    # def _apply_whitelist_split(self, text: str) -> str:
    #     print(f"START 'apply_whitelist_split'")

    #     if not self.whitelist:
    #         self.whitelist = self.preprocess_config["whitelist"]
    #         # return text

    #     self.whitelist_lower = [w.lower() for w in self.whitelist]

    #     words = text.split()
    #     result = []

    #     for word in words:
    #         split_words = self._split_with_whitelist_multi(word)

    #         if len(split_words) > 1:
    #             self.stats.whitelist_splits += 1

    #         result.extend(split_words)

    #     return " ".join(result)


    # def _split_with_whitelist_multi(self, word: str) -> str:
    #     if len(word) < 8:
    #         return [word]
        
    #     word_lower = word.lower()
    #     matches = []

    #     for w_lower, w in zip(self.whitelist_lower, 
    #                           self.whitelist):
    #         # w_lower = w.lower()
    #         start = 0

    #         while True:
    #             idx = word_lower.find(w_lower, start)
    #             if idx == -1:
    #                 break

    #             matches.append((idx, idx + len(w)))
    #             start = idx + 1
        
    #     if not matches: 
    #         return [word]
        
    #     matches.sort()

    #     result = []
    #     last_idx = 0

    #     for start, end in matches:
    #         if start > last_idx:
    #             result.append(word[last_idx:start])

    #         result.append(word[start:end])
    #         last_idx = end

    #     if last_idx < len(word):
    #         result.append(word[last_idx:])

    #     return [r for r in result if r]

 
    # def text_repair_tokenizer(self, text):
    #     # lazy import
    #     from transformers import AutoTokenizer

    #     config = self.preprocess_config
    #     token_model = config["tokenizer_model"]
    #     tokenizer = AutoTokenizer.from_pretrained(token_model)

    #     tokens = tokenizer.tokenize(text)
    #     # tokens = tokenizer(text)["input_ids"]

    #     # chunks = [
    #     #     tokens[i:i+256]
    #     #     for i in range(0, len(tokens), 200)
    #     # ]

    #     return tokens
    

    