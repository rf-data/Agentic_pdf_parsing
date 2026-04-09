## text_cleaner.py
# import
import re
# import gc
from typing import List, Dict
from dataclasses import dataclass, field

# from src.core.logging import create_logger
# from src.core.session import session

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
class TextCleaner:
    f_name: str = ""
    whitelist: List[str] = field(default_factory=list)
    whitelist_lower: List[str] = field(default_factory=list)

    debug: bool = False

    stats: CleaningStats = field(default_factory=CleaningStats)

    # -------------------------
    # Public API
    # -------------------------
    def clean(self, text: str) -> str:
        text = self._basic_cleanup(text)
        text = self._fix_case_boundaries(text)
        text = self._remove_noise(text)

        if self.debug:
            self._print_stats()

        return text

    def split(self, text):
        text = self._fix_joined_words(text)
        text = self._apply_whitelist_split(text)
        text = self._final_cleanup(text)
        
        if self.debug:
            self._print_stats()

        return text
    
    # -------------------------
    # Steps
    # -------------------------
    def _basic_cleanup(self, text: str) -> str:
        print(f"START 'basic_cleanup'")

        # Fix missing white spaces after dot, colon and semicolon
        text = re.sub(r'([,;:])(?=\S)', r'\1', text)

        # 
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        text = re.sub(r'\.\s*([A-Z])', '.\n\\1', text)
        
        # multiple white spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


    def _fix_case_boundaries(self, text: str) -> str:
        print(f"START 'fix_case_boundaries'")

        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)


    def _remove_noise(self, text):
        print(f"START 'remove_noise'")

        # DOI, URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # page numbers 
        text = re.sub(r'Page \d+ / \d+', '', text)
        
        # remove section 'References'
        text = re.split(r'References:', text)[0]

        return text


    def _fix_joined_words(self, text: str) -> str:
        print(f"START 'fix_joined_words'")

        words = text.split()
        new_words = []

        k = 0
        for word in words:
            self.stats.total_words += 1

            split_word = self._smart_split(word)

            if split_word != word:
                self.stats.split_words += 1

                if k <= 5:
                    print("Word conversions:\n", word, "→", split_word)
                    k += 1

            new_words.append(split_word)

        return " ".join(new_words)
    

    def _smart_split(self, word: str) -> str:
        if not WORD_FREQ_AVAILABLE or len(word) < 8:
            return word

        for i in range(3, len(word) - 3):
            left = word[:i]
            right = word[i:]

            if (
                zipf_frequency(left, "en") > 3
                and zipf_frequency(right, "en") > 3
            ):
                return f"{left} {right}"

        return word


    def _apply_whitelist_split(self, text: str) -> str:
        print(f"START 'apply_whitelist_split'")

        if not self.whitelist:
            return text

        self.whitelist_lower = [w.lower() for w in self.whitelist]

        words = text.split()
        result = []

        for word in words:
            split_words = self._split_with_whitelist_multi(word)

            if len(split_words) > 1:
                self.stats.whitelist_splits += 1

            result.extend(split_words)

        return " ".join(result)

    # return " ".join(result)
        # prev_text = None
        # current_text = text

        # max_iter = 6

        # for _ in range(max_iter):
        #     # while in_count != out_count:
        #     if prev_text == current_text:
        #         break
                
        #     prev_text = current_text

        #     words = current_text.split()
        #     new_words = []
        #     for word in words:
        #         split = self._split_with_whitelist(word)

        #         if split != word:
        #             self.stats.whitelist_splits += 1

        #         new_words.append(split)

        #         del split
        #         gc.collect()
                
        #         # out_count = len(new_words)
        #     current_text = " ".join(new_words)
            
        #     if self.debug:
        #         print(f"[Whitelist Iteration] {_}: {current_text[:100]}")

        #     # words = new_text.split()
        #     # in_count = len(words)

        # return current_text


    def _split_with_whitelist_multi(self, word: str) -> str:
        if len(word) < 8:
            return [word]
        
        word_lower = word.lower()
        matches = []

        for w_lower, w in zip(self.whitelist_lower, self.whitelist):
            # w_lower = w.lower()
            start = 0

            while True:
                idx = word_lower.find(w_lower, start)
                if idx == -1:
                    break

                matches.append((idx, idx + len(w)))
                start = idx + 1
        
        if not matches: 
            return [word]
        
        matches.sort()

        result = []
        last_idx = 0

        for start, end in matches:
            if start > last_idx:
                result.append(word[last_idx:start])

            result.append(word[start:end])
            last_idx = end

        if last_idx < len(word):
            result.append(word[last_idx:])

        return [r for r in result if r]
    
        #     if 0 < idx < len(word) - len(w):
        #         left = word[:idx]
        #         right = word[idx:]
        #         return f"{left} {right}"

        # return word


    def _final_cleanup(self, text: str) -> str:
        print(f"START 'final_cleanup'")

        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # -------------------------
    # Debugging
    # -------------------------
    def _print_stats(self):
        # logger = session.logger

        # logger.info("""
        # --- TextCleaner Stats ---)
        # Total words processed: %s
        # Word splits (freq):    %s                    
        # Whitelist splits:      %s  
        # ------------------------                  
        # """,
        # self.stats.total_words, 
        # self.stats.split_words,
        # self.stats.whitelist_splits
        # )

        print(f"""
--- TextCleaner Stats ({self.f_name}) ---
Total words processed: {self.stats.total_words}
Word splits (freq):    {self.stats.split_words}                    
Whitelist splits:      {self.stats.whitelist_splits}
------------------------                  
""")