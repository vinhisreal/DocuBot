import os
import shutil
import uuid
import ast 
from fastapi import UploadFile

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.models.document import Document 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
FAISS_INDEX_PATH = "faiss_index"

class RAGService:
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        self.embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")

        if os.path.exists(FAISS_INDEX_PATH):
            self.vector_db = FAISS.load_local(
                FAISS_INDEX_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
        else:
            self.vector_db = FAISS.from_texts(["init"], self.embeddings)
            self.vector_db.delete([self.vector_db.index_to_docstore_id[0]])

        self.last_topic = None

        prompt = ChatPromptTemplate.from_template("""
            Bạn là trợ lý AI chuyên nghiệp. Hãy trả lời câu hỏi dựa trên ngữ cảnh sau:
            <context>
            {context}
            </context>
            Câu hỏi: {input}
        """)
        self.document_chain = create_stuff_documents_chain(self.llm, prompt)

    async def ingest_file(self, file: UploadFile, db: AsyncSession):
        doc_id = str(uuid.uuid4())
        
        new_doc = Document(id=doc_id, filename=file.filename)
        db.add(new_doc)
        await db.commit()

        temp = f"temp_{file.filename}"
        with open(temp, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            loader = PyPDFLoader(temp)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = splitter.split_documents(docs)

            for s in splits:
                s.metadata["source"] = doc_id
                s.metadata["original_name"] = file.filename

            self.vector_db.add_documents(splits)
            self.vector_db.save_local(FAISS_INDEX_PATH)

            return {
                "id": doc_id,
                "filename": file.filename,
                "chunks_count": len(splits),
                "message": "OK"
            }
        finally:
            if os.path.exists(temp): os.remove(temp)

    async def list_files(self, db: AsyncSession):
        result = await db.execute(select(Document))
        docs = result.scalars().all()
        return [{"id": d.id, "filename": d.filename} for d in docs]

    async def delete_file(self, doc_id: str, db: AsyncSession):
        query = delete(Document).where(Document.id == doc_id)
        res = await db.execute(query)
        await db.commit()
        
        if res.rowcount == 0:
            return "File not found in DB"

        docstore = self.vector_db.docstore._dict
        ids_to_delete = [k for k, v in docstore.items() if v.metadata.get("source") == doc_id]
        
        if ids_to_delete:
            self.vector_db.delete(ids_to_delete)
            self.vector_db.save_local(FAISS_INDEX_PATH)

        return f"Deleted document {doc_id}"

    async def chat(self, query: str, db: AsyncSession):
        topic = self.llm.invoke(f"""
            Classify topic (1 word only): "{query}"
        """).content.strip().lower()

        changed = (topic != self.last_topic)
        self.last_topic = topic

        db_files = await self.list_files(db)
        all_filenames = [f['filename'] for f in db_files]

        if not all_filenames:
             return {"answer": "Chưa có tài liệu nào.", "sources": []}

        router_res = self.llm.invoke(f"""
            Question: "{query}"
            Files: {all_filenames}
            Return python list of relevant filenames.
        """)
        
        try:
            relevant_files = ast.literal_eval(router_res.content.strip())
            if not isinstance(relevant_files, list): relevant_files = all_filenames
        except:
            relevant_files = all_filenames

        retriever = self.vector_db.as_retriever(
            search_kwargs={
                "k": 5,
                "fetch_k": 50, 
                "filter": lambda metadata: metadata.get("original_name") in relevant_files
            }
        )

        chain = create_retrieval_chain(retriever, self.document_chain)
        res = chain.invoke({"input": query})

        sources = list({
            d.metadata.get("original_name")
            for d in res.get("context", [])
        })

        return {
            "answer": res["answer"],
            "sources": sources,
            "topic": topic,
            "topic_changed": changed
        }
    async def reset_database(self, db: AsyncSession):
        """Xóa sạch sành sanh SQL và Vector DB"""
        
        await db.execute(delete(Document)) 
        await db.commit()

        self.vector_db = FAISS.from_texts(["init"], self.embeddings)
        self.vector_db.delete([self.vector_db.index_to_docstore_id[0]])
        self.vector_db.save_local(FAISS_INDEX_PATH)

        return "System reset successfully!"