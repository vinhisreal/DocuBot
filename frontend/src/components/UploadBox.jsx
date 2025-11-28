import axios from "axios";
import { useState } from "react";

export default function UploadBox() {
  const [file, setFile] = useState(null);

  const uploadPdf = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("http://localhost:8000/api/v1/rag/ingest", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    alert("Ingested successfully!");
  };

  return (
    <div className="my-4">
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0])}
        className="text-white"
      />

      <button
        onClick={uploadPdf}
        className="ml-3 px-3 py-1 bg-blue-500 text-white rounded"
      >
        Upload PDF
      </button>
    </div>
  );
}
