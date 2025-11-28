import os
import shutil
import uuid  # <--- Import thư viện tạo ID
from fastapi import UploadFile

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.schemas.rag import DocumentInfo # Import schema mới

PERSIST_DIRECTORY = "./chroma_db"

class RAGService:
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_db = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )

    async def ingest_file(self, file: UploadFile):
        # 1. Tạo UUID duy nhất cho file này
        doc_id = str(uuid.uuid4())
        
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # 2. GẮN METADATA ID VÀO TỪNG CHUNK
            # Đây là bước quan trọng nhất: Ghi đè metadata
            for split in splits:
                split.metadata["source"] = doc_id          # source giờ là ID
                split.metadata["original_name"] = file.filename # Lưu tên gốc để hiển thị
            
            self.vector_db.add_documents(documents=splits)
            
            return {
                "id": doc_id,
                "filename": file.filename,
                "message": "Ingest successfully!",
                "chunks_count": len(splits)
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def list_files(self):
        """Lấy danh sách file dựa trên ID"""
        data = self.vector_db.get()
        metadatas = data.get('metadatas', [])
        
        # Dùng dictionary để lọc trùng theo ID: { "uuid-123": "cv.pdf" }
        unique_docs = {}
        
        if metadatas:
            for meta in metadatas:
                if meta:
                    doc_id = meta.get('source') # Lấy ID
                    doc_name = meta.get('original_name', 'Unknown') # Lấy tên gốc
                    
                    if doc_id and doc_id not in unique_docs:
                        unique_docs[doc_id] = doc_name
        
        # Convert về list object
        results = []
        for doc_id, doc_name in unique_docs.items():
            results.append(DocumentInfo(id=doc_id, filename=doc_name))
            
        return results

    async def delete_file(self, doc_id: str): # Tham số vào là ID
        """Xóa file theo ID"""
        try:
            # Xóa theo metadata 'source' (chính là doc_id)
            self.vector_db.delete(where={"source": doc_id})
            return f"Đã xóa tài liệu có ID: {doc_id}"
        except Exception as e:
            return f"Lỗi khi xóa: {str(e)}"

    async def chat(self, query: str):
        # ... (Phần tạo prompt giữ nguyên) ...
        prompt = ChatPromptTemplate.from_template("""
            Bạn là trợ lý AI chuyên nghiệp. Hãy trả lời câu hỏi dựa trên ngữ cảnh sau:
            <context>
            {context}
            </context>
            Câu hỏi: {input}
        """)
        
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_db.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        response = retrieval_chain.invoke({"input": query})
        
        # --- TRÍCH XUẤT NGUỒN (Theo tên file gốc) ---
        sources = set()
        if "context" in response:
            for doc in response["context"]:
                # Lấy tên gốc từ metadata
                original_name = doc.metadata.get("original_name", "")
                if original_name:
                    sources.add(original_name)
        
        return {
            "answer": response["answer"],
            "sources": list(sources)
        }