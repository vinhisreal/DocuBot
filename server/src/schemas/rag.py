from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

class IngestResponse(BaseModel):
    filename: str
    message: str
    chunks_count: int                                                    