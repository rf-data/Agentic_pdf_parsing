## text_schema.py
# imports
from pydantic import BaseModel


class PageText(BaseModel):
    document_id: str
    page: int
    text: str

class TextChunk(BaseModel):
    document_id: str
    page: int
    chunk_id: str
    text: str
    