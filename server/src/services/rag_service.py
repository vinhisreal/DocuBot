import os
import shutil
from fastapi import UploadFile

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings

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
        """Hàm nhận file upload, lưu tạm, đọc, vector hóa"""
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            self.vector_db.add_documents(documents=splits)
            
            return {
                "filename": file.filename,
                "message": "Ingest successfully!",
                "chunks_count": len(splits)
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def chat(self, query: str) -> str:
        """Hàm trả lời câu hỏi"""
        prompt = ChatPromptTemplate.from_template("""
            Bạn là trợ lý AI chuyên nghiệp. Hãy trả lời dựa trên ngữ cảnh (context) sau:
            <context>
            {context}
            </context>
            Câu hỏi: {input}
        """)
        
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_db.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        response = retrieval_chain.invoke({"input": query})
        return response["answer"]