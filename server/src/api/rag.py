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

# 1. Khởi tạo Database khi app chạy (Tạo bảng nếu chưa có)
@router.on_event("startup")
async def startup_event():
    await init_db()

# 2. API Ingest (Cần DB để lưu metadata)
@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) # <--- Inject DB Session
):
    return await service.ingest_file(file, db)

# 3. API List Files (Lấy từ SQL -> Siêu nhanh)
@router.get("/files", response_model=ListFilesResponse)
async def get_all_documents(
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) # <--- Inject DB Session
):
    docs = await service.list_files(db)
    return ListFilesResponse(
        documents=docs, 
        count=len(docs)
    )

# 4. API Chat (Cần DB để Router lấy danh sách file)
@router.post("/chat", response_model=ChatResponse)
async def chat_document(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) # <--- Inject DB Session
):
    result = await service.chat(request.query, db)
    return ChatResponse(answer=result["answer"], sources=result["sources"])

# 5. API Delete (Xóa SQL + FAISS)
@router.delete("/files/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str, 
    service: RAGService = Depends(get_rag_service),
    db: AsyncSession = Depends(get_db) # <--- Inject DB Session
):
    message = await service.delete_file(doc_id, db)
    return DeleteResponse(message=message)