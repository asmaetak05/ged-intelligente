import React, { useState } from 'react';
import axios from 'axios';
import { Upload as UploadIcon, File } from 'lucide-react';
import { toast } from 'sonner';

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
    if (!selectedFile) return;
    
    // UI-16: Validation
    if (!selectedFile.name.toLowerCase().endsWith('.zip') && !selectedFile.name.toLowerCase().endsWith('.rar') && !selectedFile.name.toLowerCase().endsWith('.7z')) {
      toast.error("Format de fichier non supporté. Veuillez uploader un ZIP, RAR ou 7Z.");
      return;
    }
    
    if (selectedFile.size > 50 * 1024 * 1024) {
      toast.error("Le fichier dépasse la taille maximale autorisée (50 MB).");
      return;
    }

    setFile(selectedFile);
    setProgress(10);
    
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const uploadRes = await axios.post('http://127.0.0.1:8000/api/v1/ged/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          const percent = Math.round((evt.loaded * 100) / evt.total);
          setProgress(Math.min(percent, 30)); // 30% for upload phase
        }
      });
      
      const docId = uploadRes.data.document_id;
      toast.success("Fichier uploadé avec succès. Traitement en cours...");
      
      // Real backend processing progress polling
      const interval = setInterval(async () => {
        try {
          const statusRes = await axios.get(`http://127.0.0.1:8000/api/v1/ged/documents/${docId}/preview`);
          const st = statusRes.data.status;
          
          if (st === 'UPLOADED' || st === 'EXTRACTED') {
            setProgress(60);
          } else if (st === 'OCR_PROCESSED' || st === 'NLP_PROCESSED') {
            setProgress(100);
            toast.success("Traitement terminé !");
            clearInterval(interval);
          } else if (st === 'FAILED') {
            clearInterval(interval);
            toast.error("Échec du traitement du fichier.");
          }
        } catch (e) {
          console.error(e);
        }
      }, 2000);

    } catch (err) {
      console.error("Upload failed", err);
      toast.error("Erreur lors de l'upload du fichier.");
      setProgress(0);
      setFile(null);
    }
  };

  return (
    <div className="p-8 h-full flex flex-col items-center justify-center relative">
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundColor: 'var(--color-bg-light)', opacity: 0.5 }}></div>
      <div className="w-full max-w-lg relative z-10">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-primary-dark mb-2">Pipeline d'Ingestion</h2>
          <p className="text-text-muted text-sm font-medium">Déposez un dossier compressé pour lancer le traitement OCR/NLP.</p>
        </div>

        {!file ? (
          <div 
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-md p-16 text-center transition-all cursor-pointer ${isDragging ? 'border-primary-accent bg-primary-accent/5' : 'border-border-color bg-white hover:border-primary-accent/50 hover:bg-bg-light'}`}
          >
            <UploadIcon size={36} className={`mx-auto mb-4 ${isDragging ? 'text-primary-accent' : 'text-text-muted'}`} strokeWidth={1.5} />
            <p className="text-base font-bold text-primary-dark mb-1">Cliquez ou glissez un fichier</p>
            <p className="text-xs text-text-muted">ZIP, RAR, 7Z supportés (Max 50MB)</p>
            <input type="file" className="hidden" accept=".zip" onChange={(e) => handleUpload(e.target.files[0])} />
          </div>
        ) : (
          <div className="bg-white p-6 rounded-md border border-border-color shadow-sm">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-bg-light rounded flex items-center justify-center">
                <File size={24} className="text-primary-dark" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-bold text-primary-dark">{file.name}</p>
                <p className="text-xs text-text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <span className="text-xs font-bold text-primary-accent">{progress}%</span>
            </div>
            
            <div className="space-y-4">
              {[
                { label: "Décompression", threshold: 30 },
                { label: "Extraction Textuelle", threshold: 60 },
                { label: "Vectorisation BDD", threshold: 100 }
              ].map((step, i) => (
                <div key={i}>
                  <div className="flex justify-between text-xs mb-1 font-semibold">
                    <span className={progress >= step.threshold ? 'text-primary-dark' : 'text-text-muted'}>{step.label}</span>
                  </div>
                  <div className="w-full bg-bg-light rounded-full h-1.5 overflow-hidden">
                    <div className="bg-primary-accent h-full transition-all duration-300" 
                         style={{ width: `${Math.max(0, Math.min(((progress - (i*30)) / 30) * 100, 100))}%` }}>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {progress >= 100 && (
              <button onClick={() => setFile(null)} className="w-full mt-6 bg-primary-dark text-white text-sm font-bold py-3 rounded-pill hover:bg-secondary-dark transition-all shadow-md">
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
