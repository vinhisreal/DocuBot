from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# Import các schema mới
from src.schemas.rag import ChatRequest, ChatResponse, IngestResponse, ListFilesResponse, DeleteResponse
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

@router.get("/files", response_model=ListFilesResponse)
async def get_all_documents(service: RAGService = Depends(get_rag_service)):
    docs = await service.list_files()
    return ListFilesResponse(
        documents=docs, # Trả về list object {id, filename}
        count=len(docs)
    )

@router.post("/chat", response_model=ChatResponse)
async def chat_document(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service)
):
    result = await service.chat(request.query)
    return ChatResponse(answer=result["answer"], sources=result["sources"])

@router.delete("/files/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str, 
    service: RAGService = Depends(get_rag_service)
):
    message = await service.delete_file(doc_id)
    return DeleteResponse(message=message)