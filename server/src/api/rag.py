from fastapi import APIRouter, UploadFile, File, Depends
from src.schemas.rag import ChatRequest, ChatResponse, IngestResponse
from src.services.rag_service import RAGService

router = APIRouter()

def get_rag_service():
    return RAGService()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    service: RAGService = Depends(get_rag_service)
):
    return await service.ingest_file(file)

@router.post("/chat", response_model=ChatResponse)
async def chat_document(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service)
):
    answer = await service.chat(request.query)
    return ChatResponse(answer=answer)