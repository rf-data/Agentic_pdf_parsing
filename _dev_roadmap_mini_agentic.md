

🎯 Ziel des Mini-Projekts

👉 Du brauchst kein komplexes System, sondern:

Ein kleines, sauberes, erklärbares Agent-System mit klarem Use Case

🧠 Projektidee (perfekt für deine Bewerbungen)
🔥 “Document Processing Agent (LLM + Tools)”

👉 Use Case (passt zu beiden Stellen!):

Ein Agent verarbeitet ein Dokument (PDF/Text), extrahiert strukturierte Infos und entscheidet, was damit passiert.

🏗️ Architektur (einfach, aber überzeugend)
🔹 Komponenten
Input
PDF oder Textfile
Tools (sehr wichtig!)
extract_text() → PDF/Text laden
classify_content() → z. B. Kategorie bestimmen
extract_fields() → strukturierte Infos (JSON)
decision_logic() → einfache Regel / nächste Aktion
Agent
orchestriert die Schritte
entscheidet: welches Tool wann
Output
JSON + ggf. Textsummary
🔁 Ablauf (so musst du es bauen)
Input (PDF/Text)
   ↓
Text Extraction
   ↓
LLM: Classification
   ↓
LLM: Structured Extraction
   ↓
Decision Step (Rule or LLM)
   ↓
Final Output (JSON)
⚙️ Tech Stack (minimal, aber sinnvoll)

👉 Bitte nicht overengineeren.

Python
OpenAI API (oder kompatibel)
optional: LangChain (light!)
pydantic (für Output-Struktur)
pdfplumber oder PyPDF
📁 Projektstruktur
mini_agent_project/
│
├── main.py
├── agent/
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.py
│
├── schemas/
│   └── output_schema.py
│
├── data/
│   └── sample.pdf
│
└── README.md
🔧 Kernkomponenten (Skizze)
🔹 Tool Beispiel
def extract_text(file_path: str) -> str:
    # PDF oder TXT laden
    return text
🔹 LLM Extraction
def extract_fields(text: str) -> dict:
    prompt = f"""
    Extract structured information:
    - topic
    - key_entities
    - summary
    
    Text:
    {text}
    """
    return llm_call(prompt)
🔹 Agent Logic (einfach, aber wichtig!)
def run_agent(file_path: str):
    text = extract_text(file_path)
    
    category = classify_content(text)
    
    structured = extract_fields(text)
    
    decision = make_decision(structured)
    
    return {
        "category": category,
        "data": structured,
        "decision": decision
    }

👉 Das reicht schon für CV!

🧠 Was das Projekt beweist

Wenn richtig gebaut:

✔ Tool-based architecture
✔ Multi-step workflow
✔ LLM integration
✔ Structured outputs
✔ Decision logic

👉 = genau das, was Avanade + S2 wollen

📄 README (extrem wichtig!)

Du brauchst das:

Goal:
Build a simple agent that processes unstructured documents and turns them into structured outputs.

Key Features:
- Tool-based architecture
- Multi-step processing
- LLM-based reasoning
- Structured output (JSON)
🔥 CV Formulierung danach
Document Processing Agent (LLM-based)

- Built a tool-based agent for processing unstructured documents (PDF/text)
- Implemented multi-step workflows including classification, information extraction, and decision logic
- Designed structured outputs and modular pipeline architecture
⚠️ Typische Fehler (bitte vermeiden)

❌ zu komplex (LangChain overkill)
❌ kein klares Ziel
❌ nur „LLM call“ ohne Struktur
❌ kein Output-Schema

👉 Dann ist es wertlos für Bewerbungen

🚀 Bonus (wenn du mehr willst)

Wenn du +1 Level gehst:

CLI Interface (python main.py file.pdf)
Logging
mehrere Tools auswählbar

👉 Das macht sofort „Engineer“-Eindruck

🧨 Ehrliche Einschätzung

Wenn du das sauber umsetzt:

👉 ersetzt 50 % deiner aktuellen „Agentic AI“-Claims durch echten Beweis

👉 Nächster Schritt

Wenn du bereit bist:

Sag einfach:
👉 „Code starten“

Dann bauen wir das Schritt für Schritt zusammen (copy-paste ready)
inkl. sauberer Struktur + Prompts + Output-Schema.