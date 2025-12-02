# 🤖 DocuBot - Smart RAG Chatbot

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB.svg)
![LangChain](https://img.shields.io/badge/AI-LangChain-orange.svg)

**DocuBot** is an intelligent virtual assistant system utilizing **RAG (Retrieval-Augmented Generation)** technology. It allows users to upload PDF documents and ask questions related to their content using natural language (optimized for Vietnamese). The system combines the power of **Google Gemini** for answer generation and **FAISS** for high-speed semantic search.

---

## 🚀 Key Features

- **📄 Document Ingestion:** Automatically upload, read, and chunk PDF files.
- **🔍 Hybrid Database:** A robust architecture combining:
  - **SQLite:** Fast metadata management (ID, filename, upload date).
  - **FAISS:** Vector Database for high-speed semantic search.
- **🧠 AI Powered:** Powered by the **Google Gemini 2.5 Flash** model (Large context window) for generating comprehensive and accurate answers.
- **🇻🇳 Vietnamese Optimized:** Optimized for the Vietnamese language using the **BKAI Embedding model** (`bkai-foundation-models/vietnamese-bi-encoder`).
- **💬 Smart Router:** Automatically classifies user questions and routes them to the relevant document context.
- **📝 Citation:** Provides source citations (original filename) for every answer to ensure reliability.
- **🎨 Modern UI:** A modern ReactJS (Vite) interface with Dark Mode support and Markdown rendering.

---

## 🛠️ Tech Stack

### Backend (Python)
- **Core Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async, High performance).
- **LLM Orchestration:** [LangChain](https://langchain.com/).
- **LLM Provider:** Google Gemini API (`gemini-2.5-flash`).
- **Embeddings:** HuggingFace (`sentence-transformers` / `bkai-foundation-models`).
- **Vector Store:** [FAISS](https://github.com/facebookresearch/faiss) (CPU).
- **Database:** SQLite (with `aiosqlite` & `SQLAlchemy` async).

### Frontend (JavaScript)
- **Framework:** ReactJS + Vite.
- **Styling:** TailwindCSS.
- **HTTP Client:** Axios.
- **Icons:** Lucide React.
- **Markdown:** React Markdown + Remark GFM.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher.
- Node.js 18 or higher.
- Google Gemini API Key (Get it for free at [Google AI Studio](https://aistudio.google.com/)).
### 2. Configuration (.env)
Create a .env file in the root directory of the project (same level as the src folder). You can copy the content below for Backend:
```bash
  # --- SERVER CONFIGURATION ---
  ENVIRONMENT=LOCAL
  # Allow Frontend to call API (CORS) - Add your frontend URL here
  CORS_ORIGINS=["http://localhost:3000"]
  CORS_HEADERS=["*"]

  # --- DATABASE (SQLite Async) ---
  # No installation required, file will be created automatically
  DATABASE_URL=sqlite:///./rag_app.db
  DATABASE_ASYNC_URL=sqlite+aiosqlite:///./rag_app.db

  # --- AI KEYS ---
  # Replace with your actual Google API Key
  GOOGLE_API_KEY=
```

### 2. Backend Setup

```bash
# Clone the repository
git clone [https://github.com/vinhisreal/DocuBot.git](https://github.com/vinhisreal/DocuBot.git)
cd DocuBot

# Create a virtual environment (Recommended)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (See Configuration section below)

# Run the Server
uvicorn src.main:app --reload
```
The backend server will start at: http://127.0.0.1:8000

### 3. Frontend Setup
Open a new terminal (keep the backend terminal running):
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```
