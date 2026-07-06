import React, { useState } from 'react';
import axios from 'axios';
import { Upload as UploadIcon, File } from 'lucide-react';

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files.length > 0) handleUpload(e.dataTransfer.files[0]);
  };

  const handleUpload = async (selectedFile) => {
    setFile(selectedFile);
    setProgress(10);
    
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await axios.post('http://127.0.0.1:8000/api/v1/ged/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          const percent = Math.round((evt.loaded * 100) / evt.total);
          setProgress(Math.min(percent, 30)); // 30% for upload phase
        }
      });
      
      // Simulate backend processing progress after upload
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 100) { clearInterval(interval); return 100; }
          return p + 10;
        });
      }, 500);

    } catch (err) {
      console.error("Upload failed", err);
      setProgress(0);
      setFile(null);
    }
  };

  return (
    <div className="p-8 h-full flex flex-col items-center justify-center">
      <div className="w-full max-w-lg">
        <div className="mb-8 text-center">
          <h2 className="text-xl font-medium text-zinc-900 mb-1">Pipeline d'Ingestion</h2>
          <p className="text-zinc-500 text-sm">Déposez un dossier compressé pour lancer le traitement OCR/NLP.</p>
        </div>

        {!file ? (
          <div 
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`border border-dashed rounded-md p-16 text-center transition-colors cursor-pointer ${isDragging ? 'border-zinc-900 bg-zinc-50' : 'border-zinc-300 bg-white hover:border-zinc-400'}`}
          >
            <UploadIcon size={32} className="mx-auto mb-4 text-zinc-400" strokeWidth={1.5} />
            <p className="text-sm text-zinc-900 mb-1">Cliquez ou glissez un fichier</p>
            <p className="text-xs text-zinc-500">ZIP, RAR, 7Z supportés (Max 50MB)</p>
            <input type="file" className="hidden" accept=".zip" onChange={(e) => handleUpload(e.target.files[0])} />
          </div>
        ) : (
          <div className="bg-white p-6 rounded-md border border-zinc-200">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 bg-zinc-100 rounded flex items-center justify-center">
                <File size={20} className="text-zinc-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-zinc-900">{file.name}</p>
                <p className="text-xs text-zinc-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <span className="text-xs font-medium text-zinc-500">{progress}%</span>
            </div>
            
            <div className="space-y-4">
              {[
                { label: "Décompression", threshold: 30 },
                { label: "Extraction Textuelle", threshold: 60 },
                { label: "Vectorisation BDD", threshold: 100 }
              ].map((step, i) => (
                <div key={i}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className={progress >= step.threshold ? 'text-zinc-900' : 'text-zinc-400'}>{step.label}</span>
                  </div>
                  <div className="w-full bg-zinc-100 rounded-full h-1 overflow-hidden">
                    <div className="bg-zinc-900 h-full transition-all duration-300" 
                         style={{ width: `${Math.max(0, Math.min(((progress - (i*30)) / 30) * 100, 100))}%` }}>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {progress >= 100 && (
              <button onClick={() => setFile(null)} className="w-full mt-6 bg-zinc-900 text-white text-sm font-medium py-2.5 rounded-md hover:bg-zinc-800 transition-colors">
                Nouveau Traitement
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
