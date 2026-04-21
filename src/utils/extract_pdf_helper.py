## extract_helper.py
# import
from pathlib import Path
import pdfplumber
import fitz  # PyMuPDF
from tiktoken import encoding_for_model


def extract_text_pymupdf(path, preprocess_config):
    model_name = preprocess_config["model_name"]

    f_name = Path(path).stem
    doc = fitz.open(path)

    pages_records = []
    words_records = []
    for i, page in enumerate(doc):
        # etxract text, words and tokens
        text = page.get_text("text")  
        words = page.get_text("words")  

        enc = encoding_for_model(model_name)
        n_tokens = len(enc.encode(text))
        
        # height = page.rect.height
        blocks = page.get_text("blocks")

        valid_block_ids = set()
        for k, b in enumerate(blocks):
            x0, y0, x1, y1, text, *_ = b

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

            #  remove Header/Footer
            if 50 < y0 < page.rect.height - 50:
                valid_block_ids.add(k)  # continue

#             cleaned_blocks.append(text)
        words_filtered = [w for w in words 
                          if w[5] in valid_block_ids]
        
        words_sorted = sorted(words_filtered, 
                              key=lambda w: (round(w[1], 1), 
                                             w[0]))

        text_words = " ".join([w[4] for w in words_sorted])

        pages_records.append({
            "page": i,
            "height_page": page.rect.height,
            "wdith_page": page.rect.width,
            "text_raw_simple": text,
            "text_raw": text_words,
            # "words": words_sorted,
            "n_words": len(words_sorted),
            "n_tokens": n_tokens
            # optional later:
                    # section title
                    # source file
                    # paragraph index
                    # references flag
                    # figure/table flag
            })

    return {
        "pages": pages_records, 
        "words": words_records
        }


def extract_text_plumber(file_path: str, preprocess_config: dict) -> dict:
    model_name = preprocess_config["model_name"]
    
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text(x_tolerance=2, y_tolerance=2)  # layout=True) 
            
            enc = encoding_for_model(model_name)
            n_tokens = len(enc.encode(text))
            pages.append({
                    "page": i,
                    "text_raw": text if text else []
                    })

    return {
        "pages": pages,
        "n_tokens": n_tokens
        }



"""
Gut, dass du das hinterfragst – genau hier entscheidet sich, ob du Daten sinnvoll nutzt oder nur mitschleppst.

Kurz gesagt:
👉 In der aktuellen Form bringt dir words fast nichts
👉 Aber: Daraus lassen sich sehr wertvolle strukturierte Features bauen

🧠 Was steckt wirklich in words?

Nicht „nur Wörter“, sondern:

(x0, y0, x1, y1, text, ...)

👉 Das ist Layout + Text

Und das ist der Unterschied zwischen:

❌ normalem NLP
✅ dokumentenbasiertem Verständnis (PDF, Papers, Reports)
🔥 Realistisch betrachtet

Wenn du NICHT vorhast:

Layout-Analyse
Tabellen-/Header-Erkennung
wissenschaftliche Dokumente strukturieren

👉 dann: weg damit

🟢 Aber wenn du es nutzen willst…

Dann bitte NICHT als Liste speichern, sondern als Features extrahieren

🧩 Sinnvolle Features aus words

Ich gebe dir bewusst nur Dinge, die wirklich Mehrwert bringen.

1️⃣ Text-basierte Features (low effort, high value)
🔹 Durchschnittliche Wortlänge
avg_word_len = np.mean([len(w[4]) for w in words])

👉 Indikator für:

wissenschaftlicher Text vs. einfacher Text
🔹 Großbuchstaben-Anteil
upper_ratio = sum(w[4].isupper() for w in words) / len(words)

👉 erkennt:

Überschriften
Akronyme
🔹 Zahlenanteil
digit_ratio = sum(any(c.isdigit() for c in w[4]) for w in words) / len(words)

👉 erkennt:

Tabellen
Messwerte
Referenzen
2️⃣ Layout-Features (das eigentliche Gold)
🔹 Textdichte (sehr stark!)
page_area = height * width
text_area = sum((w[2]-w[0]) * (w[3]-w[1]) for w in words)

density = text_area / page_area

👉 erkennt:

Textseite vs. Abbildung vs. Tabelle
🔹 Y-Position → Struktur erkennen
y_positions = [w[1] for w in words]

Features:

min / max / mean
std

👉 erkennt:

Header (oben)
Footer (unten)
🔹 Zeilenstruktur (wichtig!)

Cluster nach y:

👉 daraus kannst du:

Anzahl Zeilen
Zeilenlänge
Paragraph-Struktur

ableiten

3️⃣ Semantische Layout-Features (sehr stark für dein Projekt)
🔹 Header Detection (extrem nützlich!)

Heuristik:

if word[1] < threshold and word[4].isupper():

👉 typische Paper-Titel:

groß
oben
wenige Wörter
🔹 Section Detection

Erkennen von:

"INTRODUCTION"
"METHODS"
"RESULTS"

👉 oft:

eigene Zeile
Großbuchstaben
mittige Position
4️⃣ Chunk-Verbesserung (das unterschätzt du gerade)

Dein Chunking ist aktuell:

👉 rein textbasiert

Mit words kannst du:

🔹 Layout-aware Chunking
keine Chunk-Grenze mitten im Absatz
keine Trennung von Überschrift + Text

👉 das ist MASSIV besser für LLMs

⚠️ Was du NICHT tun solltest
df["words"] = words

→ das ist:

❌ Speicher-Müll
❌ nicht nutzbar
❌ verursacht genau deine Arrow-Probleme

🧭 Klare Empfehlung (ehrlich)

Für dein aktuelles Projekt:

👉 Phase 1:

DROP words

👉 Phase 2 (optional, wenn du weitergehst):

Extrahiere nur:

{
    "text_density": ...,
    "avg_word_len": ...,
    "upper_ratio": ...,
    "digit_ratio": ...,
    "n_lines": ...,
}

→ das reicht völlig

🔥 Real Talk

Du bist gerade an einem typischen Punkt:

„Ich habe viele Daten → also sind sie wertvoll“

Nein.

👉 80% davon sind Ballast
👉 20% sind Features

Deine Aufgabe ist:

👉 die 20% zu isolieren

🚀 Wenn du willst

Ich kann dir im nächsten Schritt:

👉 eine Funktion bauen:

extract_layout_features(words, page_height, page_width)
"""
