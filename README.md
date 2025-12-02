# 🤖 DocuBot - Smart RAG Chatbot

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB.svg)
![LangChain](https://img.shields.io/badge/AI-LangChain-orange.svg)

**DocuBot** là hệ thống trợ lý ảo thông minh sử dụng kỹ thuật **RAG (Retrieval-Augmented Generation)**, cho phép người dùng tải lên tài liệu PDF và hỏi đáp nội dung liên quan bằng ngôn ngữ tự nhiên (Tiếng Việt). Hệ thống kết hợp sức mạnh của **Google Gemini** để sinh câu trả lời và **FAISS** để tìm kiếm ngữ nghĩa tốc độ cao.

---

## 🚀 Tính năng chính

- **📄 Ingest Documents:** Tải lên, đọc và phân mảnh (chunking) file PDF tự động.
- **🔍 Hybrid Database:** Kiến trúc lai kết hợp:
  - **SQLite:** Quản lý metadata file (ID, tên, ngày tạo) nhanh chóng.
  - **FAISS:** Vector Database lưu trữ ngữ nghĩa văn bản để tìm kiếm siêu tốc.
- **🧠 AI Powered:** Sử dụng mô hình **Google Gemini 2.5 Flash** (Context window lớn) để tổng hợp câu trả lời.
- **🇻🇳 Vietnamese Optimized:** Tối ưu hóa cho tiếng Việt với model Embedding **BKAI (bkai-foundation-models/vietnamese-bi-encoder)**.
- **💬 Smart Router:** Tự động phân loại câu hỏi và định tuyến đến đúng tài liệu cần tìm.
- **📝 Citation:** Trích dẫn nguồn (tên file gốc) cho mỗi câu trả lời để đảm bảo độ tin cậy.
- **🎨 Modern UI:** Giao diện ReactJS (Vite) hiện đại, hỗ trợ Dark Mode, Markdown rendering.

---

## 🛠️ Công nghệ sử dụng

### Backend (Python)
- **Core Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async, High performance).
- **LLM Orchestration:** [LangChain](https://langchain.com/).
- **LLM Provider:** Google Gemini API (`gemini-2.5-flash`).
- **Embeddings:** HuggingFace (`sentence-transformers` / `bkai-foundation-models`).
- **Vector Store:** [FAISS](https://github.com/facebookresearch/faiss) (CPU).
- **Database:** SQLite (với `aiosqlite` & `SQLAlchemy` async).

### Frontend (JavaScript)
- **Framework:** ReactJS + Vite.
- **Styling:** TailwindCSS.
- **HTTP Client:** Axios.
- **Icons:** Lucide React.
- **Markdown:** React Markdown + Remark GFM.

---

## ⚙️ Cài đặt & Chạy dự án

### 1. Yêu cầu tiên quyết (Prerequisites)
- Python 3.10 trở lên.
- Node.js 18 trở lên.
- API Key Google Gemini (Lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/)).

### 2. Thiết lập Backend

```bash
# Clone dự án
git clone [https://github.com/vinhisreal/DocuBot.git](https://github.com/vinhisreal/DocuBot.git)
cd DocuBot

# Tạo môi trường ảo (Khuyến nghị)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình biến môi trường (Xem mục Cấu hình bên dưới)
# Chạy Server
uvicorn src.main:app --reload

### 3. Thiết lập Frontend

Mở một terminal mới (không tắt terminal backend):

```bash
# 1. Vào thư mục frontend
cd frontend

# 2. Cài đặt các thư viện (Node Modules)
npm install

# 3. Chạy giao diện ở chế độ Developer
npm run dev