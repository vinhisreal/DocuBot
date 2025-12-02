import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import axios from "axios";
import {
  Send,
  Menu,
  Plus,
  User,
  Sparkles,
  StopCircle,
  Trash2,
  FileText,
} from "lucide-react"; 
import UploadBox from "./components/UploadBox";

const API_BASE = "http://127.0.0.1:8000/api/v1/rag";

export default function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Xin chào! Tôi là AI trợ lý tài liệu. Bạn cần giúp gì hôm nay?",
    },
  ]);
  const [isLoading, setLoading] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [files, setFiles] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchFiles = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/files`);
      setFiles(res.data.documents || []);
    } catch (err) {
      console.error("Lỗi load file:", err);
    }
  }, []); 
  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]); 

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Xóa file "${filename}"? AI sẽ quên kiến thức này.`))
      return;

    try {
      await axios.delete(`${API_BASE}/files/${docId}`);
      fetchFiles(); 
    } catch (err) {
      console.error("Lỗi xóa file:", err);
      alert("Xóa thất bại!");
    }
  };

  const sendMessage = async () => {
    if (!query.trim()) return;

    const newMessage = { role: "user", text: query };
    setMessages((prev) => [...prev, newMessage]);
    setQuery("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        query: newMessage.text,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.data.answer,
          sources: res.data.sources, 
        },
      ]);
    } catch (err) {
      console.log(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "⚠️ Xin lỗi, có lỗi xảy ra khi kết nối server.",
        },
      ]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-[#131314] text-gray-200 font-sans overflow-hidden">
      {/* --- SIDEBAR --- */}
      <div
        className={`${
          isSidebarOpen ? "w-72" : "w-0"
        } bg-[#1E1F20] transition-all duration-300 flex flex-col border-r border-gray-800 overflow-hidden`}
      >
        <div className="p-4 flex flex-col h-full">
          <div
            onClick={() => setMessages([])}
            className="flex items-center gap-3 bg-[#282A2C] hover:bg-[#37393B] p-3 rounded-full cursor-pointer transition-colors mb-6 text-sm font-medium text-gray-300 select-none"
          >
            <Plus size={18} />
            <span>Cuộc trò chuyện mới</span>
          </div>

          <div className="mb-4">
            <p className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wider pl-2">
              Tài liệu
            </p>
            <UploadBox onUploadSuccess={fetchFiles} />
          </div>

          {/* Danh sách file */}
          <div className="flex-1 overflow-y-auto space-y-1 pr-1">
            {files.length === 0 && (
              <p className="text-xs text-gray-600 text-center mt-4">
                Chưa có tài liệu
              </p>
            )}

            {files.map((doc) => (
              <div
                key={doc.id}
                className="group flex items-center justify-between p-2 hover:bg-[#282A2C] rounded-lg cursor-pointer transition-colors"
                title={doc.filename}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <FileText size={14} className="text-gray-500 flex-shrink-0" />
                  <span className="text-xs text-gray-300 truncate max-w-[160px]">
                    {doc.filename}
                  </span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(doc.id, doc.filename);
                  }}
                  className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition p-1 hover:bg-[#37393B] rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-auto pt-4 text-[10px] text-gray-600 text-center border-t border-gray-800">
            Powered by Vinhisreal
          </div>
        </div>
      </div>

      {/* --- MAIN CHAT AREA --- */}
      <div className="flex-1 flex flex-col relative bg-[#131314]">
        {/* Header Mobile */}
        <div className="p-4 flex items-center justify-between absolute top-0 left-0 right-0 z-10 bg-[#131314]/80 backdrop-blur-sm">
          <button
            onClick={() => setSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-[#282A2C] rounded-full transition-colors text-gray-400"
          >
            <Menu size={20} />
          </button>
          <span className="font-semibold text-gray-300 opacity-0 md:opacity-100 transition-opacity text-sm">
            Document ChatBot
          </span>
          <div className="w-8"></div>
        </div>

        {/* Khu vực hiển thị tin nhắn */}
        <div className="mt-0 flex-1 overflow-y-auto p-4 pt-16 pb-32 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
          <div className="max-w-3xl mx-auto space-y-8">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {/* Avatar AI */}
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-red-500 flex items-center justify-center flex-shrink-0 mt-1">
                    <Sparkles size={16} className="text-white" />
                  </div>
                )}

                {/* Nội dung tin nhắn */}
                <div
                  className={`max-w-[85%] ${
                    msg.role === "user"
                      ? "bg-[#282A2C] rounded-2xl rounded-tr-sm px-5 py-3 text-gray-100"
                      : "px-2 py-1 text-gray-100"
                  }`}
                >
                  <div className="prose prose-invert prose-p:leading-relaxed prose-pre:bg-[#1E1F20] prose-pre:rounded-lg max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.text}
                    </ReactMarkdown>
                  </div>

                  {/* NGUỒN THAM KHẢO */}
                  {msg.role === "assistant" &&
                    msg.sources &&
                    msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-800/50">
                        <p className="text-[10px] text-gray-500 font-bold mb-2 uppercase tracking-wider flex items-center gap-1">
                          <Sparkles size={10} /> Nguồn tham khảo:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {msg.sources.map((src, i) => (
                            <span
                              key={i}
                              className="text-[10px] bg-[#1E1F20] text-blue-400 px-2 py-1 rounded border border-gray-700/50 hover:border-blue-500/50 transition-colors cursor-default truncate max-w-[200px]"
                              title={src}
                            >
                              📄 {src}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                </div>

                {/* Avatar User */}
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0 mt-1">
                    <User size={16} className="text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading */}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-red-500 flex items-center justify-center flex-shrink-0 animate-spin-slow">
                  <Sparkles size={16} className="text-white" />
                </div>
                <div className="flex items-center gap-1 h-8">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* --- INPUT AREA --- */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#131314] via-[#131314] to-transparent pt-10 pb-6 px-4">
          <div className="max-w-3xl mx-auto bg-[#1E1F20] rounded-full flex items-center px-2 py-2 border border-gray-700/50 focus-within:border-gray-500 focus-within:bg-[#282A2C] transition-all shadow-xl">
            <div className="p-2 rounded-full hover:bg-gray-700 cursor-pointer transition text-gray-400">
              <Plus size={20} />
            </div>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none ml-2 text-base"
              placeholder="Hỏi bất cứ điều gì về tài liệu..."
              disabled={isLoading}
              autoFocus
            />
            <button
              onClick={sendMessage}
              disabled={!query.trim() || isLoading}
              className={`ml-2 p-2 rounded-full transition-all ${
                query.trim()
                  ? "bg-white text-black hover:bg-gray-200"
                  : "bg-transparent text-gray-500 cursor-not-allowed"
              }`}
            >
              {isLoading ? <StopCircle size={20} /> : <Send size={20} />}
            </button>
          </div>
          <p className="text-center text-[11px] text-gray-500 mt-3 font-medium">
            DocuBot có thể hiển thị thông tin không chính xác, hãy kiểm chứng
            lại.
          </p>
        </div>
      </div>
    </div>
  );
}
