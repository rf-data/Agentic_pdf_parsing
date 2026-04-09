## tools.py
# import
# import pdfplumber

# Tool 2: Dokumenttyp klassifizieren
def classify_content():


    return 

# Tool 3: Felder extrahieren
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

# Tool 4: Validierung
def validate():

    return 


# Tool 5: Entscheidungslogik
def make_decision():

    """
    Wenn confidence < 0.7 → needs_review = True
    Wenn missing_fields nicht leer → needs_review = True
    Wenn Dokumenttyp unbekannt → manual_triage
    Sonst → store_structured_output
    """
    return 