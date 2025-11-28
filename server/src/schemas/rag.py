from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- MODEL MỚI CHO DOCUMENT ---
class DocumentInfo(BaseModel):
    id: str
    filename: str

class ListFilesResponse(BaseModel):
    documents: List[DocumentInfo] # Trả về cả ID và Tên
    count: int

class IngestResponse(BaseModel):
    id: str       # Trả về ID vừa tạo
    filename: str
    message: str
    chunks_count: int

class DeleteResponse(BaseModel):
    message: str