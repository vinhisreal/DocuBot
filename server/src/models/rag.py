from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    topic: str | None = None
    topic_changed: bool | None=None

class DocumentInfo(BaseModel):
    id: str
    filename: str

class ListFilesResponse(BaseModel):
    documents: List[DocumentInfo] 
    count: int

class IngestResponse(BaseModel):
    id: str       
    filename: str
    message: str
    chunks_count: int

class DeleteResponse(BaseModel):
    message: str