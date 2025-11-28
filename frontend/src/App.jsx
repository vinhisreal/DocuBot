import { useState } from "react";
import axios from "axios";
import UploadBox from "./components/UploadBox";

export default function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!query.trim()) return;

    const newMessage = { role: "user", text: query };
    setMessages([...messages, newMessage]);
    setQuery("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/api/v1/rag/chat", {
        query: newMessage.text,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer },
      ]);
    } catch (err) {
      console.log(err);
    }

    setLoading(false);
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-900">
      <div className="w-full max-w-xl bg-gray-800 p-5 rounded-lg shadow-md">
        <h1 className="text-white text-2xl font-bold mb-2">
          RAG Chatbot 🤖
        </h1>

        {/* ⭐ THÊM NÈ */}
        <UploadBox />

        <div className="h-[400px] overflow-y-auto bg-gray-700 p-3 rounded-md">
          {messages.map((msg, idx) => (
            <p
              key={idx}
              className={`mb-2 p-2 rounded-md ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-600 text-white"
              }`}
            >
              {msg.text}
            </p>
          ))}

          {isLoading && (
            <p className="text-gray-400 italic">AI is thinking...</p>
          )}
        </div>

        <div className="flex mt-4 gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 p-2 rounded bg-gray-700 text-white"
            placeholder="Ask something..."
          />

          <button
            onClick={sendMessage}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
