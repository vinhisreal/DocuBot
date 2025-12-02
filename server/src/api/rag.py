from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from src.models.rag import ChatRequest, ChatResponse, IngestResponse, ListFilesResponse, DeleteResponse
from src.services.rag_service import RAGService
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession 
from src.database import get_db, init_db 

router = APIRouter()

@lru_cache
def get_rag_service():
    return RAGService()

@router.on_event("startup")
async def startup_event():
    await init_db()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) 
):
    return await service.ingest_file(file, db)

@router.get("/files", response_model=ListFilesResponse)
async def get_all_documents(
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) 
):
    docs = await service.list_files(db)
    return ListFilesResponse(
        documents=docs, 
        count=len(docs)
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_document(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) 
):
    result = await service.chat(request.query, db)
    return ChatResponse(answer=result["answer"], sources=result["sources"])

@router.delete("/files/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str, 
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) 
):
    message = await service.delete_file(doc_id, db)
    return DeleteResponse(message=message)
@router.delete("/reset", response_model=DeleteResponse)
async def reset_system(
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db)
):
    message = await service.reset_database(db)
    return DeleteResponse(message=message)