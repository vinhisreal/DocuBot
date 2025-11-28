import { useState, useRef } from "react";
import axios from "axios";
import { Upload, FileText, X, CheckCircle, Loader2, AlertCircle } from "lucide-react";

const API_INGEST_URL = "http://localhost:8000/api/v1/rag/ingest";

export default function UploadBox({ onUploadSuccess, onError }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus("idle");
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        setStatus("idle");
      } else {
        if (onError) onError("Vui lòng chỉ chọn file PDF!");
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(API_INGEST_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      setStatus("success");
      setFile(null); // Reset file
      
      // Gọi callback để báo cho App biết
      if (onUploadSuccess) onUploadSuccess(file.name);

      setTimeout(() => setStatus("idle"), 3000); // Tự reset trạng thái sau 3s
    } catch (error) {
      console.error(error);
      setStatus("error");
      if (onError) onError("Lỗi khi tải file lên server.");
    } finally {
      setIsUploading(false); // Lưu ý: biến này chưa khai báo, dùng setStatus thay thế bên dưới
    }
  };
  
  // Fix lỗi logic nhỏ: setStatus("uploading") đã thay thế setIsUploading
  const isUploading = status === "uploading";

  const clearFile = () => {
    setFile(null);
    setStatus("idle");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* --- TRẠNG THÁI 1: CHƯA CHỌN FILE --- */}
      {!file && status !== "success" && (
        <div
          className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
            dragActive
              ? "border-blue-500 bg-blue-500/10"
              : "border-gray-700 hover:border-gray-500 hover:bg-[#282A2C]"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="bg-[#1E1F20] p-3 rounded-full mb-3 shadow-md">
            <Upload size={20} className="text-blue-400" />
          </div>
          <p className="text-sm font-medium text-gray-300">Tải lên PDF</p>
          <p className="text-[10px] text-gray-500 mt-1">Kéo thả hoặc click</p>
        </div>
      )}

      {/* --- TRẠNG THÁI 2: ĐÃ CHỌN FILE --- */}
      {file && status !== "success" && (
        <div className="bg-[#282A2C] rounded-xl p-3 border border-gray-700 animate-in fade-in slide-in-from-bottom-2">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="bg-red-500/20 p-2 rounded-lg">
                <FileText size={18} className="text-red-400" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-medium text-gray-200 truncate max-w-[140px]">
                  {file.name}
                </span>
                <span className="text-[10px] text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            </div>
            <button
              onClick={clearFile}
              disabled={isUploading}
              className="text-gray-500 hover:text-white p-1 rounded-full hover:bg-gray-700 transition"
            >
              <X size={16} />
            </button>
          </div>

          <button
            onClick={handleUpload}
            disabled={isUploading}
            className={`w-full py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-all ${
              isUploading
                ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20"
            }`}
          >
            {isUploading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Đang xử lý...
              </>
            ) : (
              "Bắt đầu học"
            )}
          </button>
          
          {status === "error" && (
             <div className="mt-2 text-xs text-red-400 flex items-center gap-1 justify-center">
                <AlertCircle size={12}/> Lỗi upload
             </div>
          )}
        </div>
      )}

      {/* --- TRẠNG THÁI 3: THÀNH CÔNG --- */}
      {status === "success" && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 flex flex-col items-center animate-in zoom-in duration-300">
          <CheckCircle size={32} className="text-green-400 mb-2" />
          <p className="text-sm font-semibold text-green-400">Hoàn tất!</p>
          <button
            onClick={() => setStatus("idle")}
            className="mt-3 text-xs text-gray-400 hover:text-white underline"
          >
            Thêm tài liệu khác
          </button>
        </div>
      )}
    </div>
  );
}