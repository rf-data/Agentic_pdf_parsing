# 🧠 Multi-Document Analysis with LLM & Agentic Pipeline
This project implements an agent-based system for structured analysis of scientific documents (PDFs).
It combines LLM-based extraction, deterministic aggregation, and rule-based decision-making to derive insights across multiple documents.

In scope of this project, three publically available research papers were used:   
- [Beyond_DA_hypothesis...](https://pubmed.ncbi.nlm.nih.gov/29954475/),   
- [New_atypical_antipsychotics...](https://pubmed.ncbi.nlm.nih.gov/36142523/),
- [Presynaptic_5-HT-receptors...](https://pubmed.ncbi.nlm.nih.gov/36230998/)

## 🚀 Core Idea
Instead of querying documents individually, the system:   
- Extracts structured information from each document (LLM)   
- Aggregates patterns across documents   
- Generates decisions and recommendations based on evidence

__👉 Result: A lightweight research support system__

## 🎯 Potential use cases   
- Literature review support   
- Hypothesis generation   
- Multi-document comparison   
- Research summarization

## 🏗️ Architecture Overview
![Overview workflow](/workflow.png)

## ⚙️ Pipeline Components
### 1. Extraction Engine (LLM + Cache)
Uses LLM to extract structured data from raw text
Enforces schema validation via Pydantic
Implements caching to avoid repeated API calls

__*👉 Important behavior:*__   
- LLM is only called once per unique input   
- Subsequent runs load from cache

[Example extraction response](/report/2026-04-10_11-59-06_presynaptic_5-HT_receptors_response_extract.json)

### 2_A. Deterministic Pre-Aggregation Engine
Identifies:   
- common entities   
- dominant mechanisms   
- consensus vs conflicting findings   
- Uses deterministic logic (set operations + frequency analysis)

__*👉 Goal: pattern detection across documents + secondary signal for aggregation by LLM*__

### 2_B LLM Aggregation Engine
Evaluates the info extracted from the provided files and looks for semantical similarities between the files' info.
Takes into account the pre-aggregrated info from the deterministic engine when evaluating and/or drawing conclusions from:   
- documents' main topic
- consenus points
- conflicting points   
- dominant mechanisms   
- subgroup suggestions
- evidence gaps   
- overall interpretation

[Example aggregation response](/report/2026-03-31_13-58-36_response_aggregated.json)

### 3. Decision Engine
Translates aggregated signals into:   
- conclusions   
- risks   
- recommendations

__*Key signals:*__   
- number of documents   
- consensus vs conflict   
- document quality

__*👉 Important concept:*__
Lack of consensus is treated as signal, not failure

[Example report (from v0.1)](/report/2026-03-31_13-58-36_response_aggregated.json)

## 🧠 Design Principles   
- **Separation of concerns:** Extraction ≠ Aggregation ≠ Decision   
- **LLM as component, not system:** deterministic layers around it   
- **Schema-first design:** strict validation of outputs   
- **Cache-first strategy:** reproducibility + cost control

## ⚠️ Limitations
This system is intentionally simple in some areas:   
- *Aggregation* is currently *string-based* (no semantic matching)   
- No embedding similarity yet   
- Decision layer is rule-based (not learned)

__*👉 Meaning:*__
Output quality depends heavily on extraction consistency

### 🧩 Tech Stack   
- Python   
- OpenAI API   
- Pydantic   
- JSON-based caching / reports

