import React, { useEffect, useRef, useState } from 'react';
import { Upload as UploadIcon, File } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '../api/axios';

const MAX_UPLOAD_SIZE = 50 * 1024 * 1024;
const STATUS_STEPS = {
  raw_zip: 30,
  extracted: 65,
  ocr_processed: 100,
};

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const fileInputRef = useRef(null);
  const pollingRef = useRef(null);

  const stopPolling = () => {
    if (pollingRef.current) {
      window.clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  useEffect(() => stopPolling, []);

  const startPolling = (documentId) => {
    stopPolling();
    pollingRef.current = window.setInterval(async () => {
      try {
        const response = await apiClient.get(`/api/v1/ged/documents/${documentId}/preview`);
        const nextStatus = response.data.status;
        setStatus(nextStatus);

        if (nextStatus === 'failed') {
          stopPolling();
          toast.error('Échec du traitement du fichier.');
          return;
        }

        const nextProgress = STATUS_STEPS[nextStatus] || 30;
        setProgress(nextProgress);
        if (nextStatus === 'ocr_processed') {
          stopPolling();
          toast.success('Traitement terminé : OCR et indexation effectués.');
        }
      } catch (error) {
        stopPolling();
        toast.error('Le statut du traitement ne peut pas être consulté.');
        console.error(error);
      }
    }, 1500);
  };

  const handleUpload = async (selectedFile) => {
    if (!selectedFile) return;
    const nameLower = selectedFile.name.toLowerCase();
    const isAllowed = nameLower.endsWith('.zip') || nameLower.endsWith('.pdf') || nameLower.endsWith('.docx');
    if (!isAllowed) {
      toast.error('Formats acceptés : ZIP, PDF ou DOCX.');
      return;
    }
    if (selectedFile.size > MAX_UPLOAD_SIZE) {
      toast.error('Le fichier dépasse la taille maximale autorisée (50 Mo).');
      return;
    }

    setFile(selectedFile);
    setProgress(5);
    setStatus('upload');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await apiClient.post('/api/v1/ged/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          if (!event.total) return;
          setProgress(Math.min(Math.round((event.loaded * 100) / event.total), 30));
        },
      });
      setProgress(response.data.status === 'ocr_processed' ? 100 : 30);
      setStatus(response.data.status);
      toast.success(response.data.message || 'Fichier importé. Traitement en cours…');

      if (response.data.status !== 'ocr_processed') startPolling(response.data.document_id);
    } catch (error) {
      setProgress(0);
      setStatus('failed');
      setFile(null);
      const errMsg = error.response?.data?.detail || 'Erreur lors de l’envoi du fichier. Vérifiez votre connexion ou authentification.';
      toast.error(errMsg);
      console.error(error);
    }
  };

  const reset = () => {
    stopPolling();
    setFile(null);
    setProgress(0);
    setStatus('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="p-8 h-full flex flex-col items-center justify-center">
      <div className="w-full max-w-lg">
        <div className="mb-8 text-center">
          <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100 mb-1">Pipeline d’ingestion</h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm">Importez une archive ZIP ou un fichier PDF/DOCX pour lancer l’extraction OCR et NLP.</p>
        </div>

        {!file ? (
          <div
            role="button"
            tabIndex={0}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') fileInputRef.current?.click();
            }}
            onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragging(false);
              handleUpload(event.dataTransfer.files[0]);
            }}
            className={`border border-dashed rounded-md p-16 text-center transition-colors cursor-pointer ${isDragging ? 'border-zinc-900 dark:border-zinc-100 bg-zinc-50 dark:bg-zinc-800' : 'border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800/50 hover:border-zinc-400 dark:hover:border-zinc-500'}`}
          >
            <UploadIcon size={32} className="mx-auto mb-4 text-zinc-400 dark:text-zinc-500" strokeWidth={1.5} />
            <p className="text-sm text-zinc-900 dark:text-zinc-100 mb-1">Cliquez ou glissez un fichier (ZIP, PDF, DOCX)</p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Formats : ZIP, PDF, DOCX — taille max : 50 Mo</p>
            <input ref={fileInputRef} type="file" className="hidden" accept=".zip,.pdf,.docx,application/zip,application/pdf" onChange={(event) => handleUpload(event.target.files?.[0])} />
          </div>
        ) : (
          <div className="bg-white dark:bg-zinc-800 p-6 rounded-md border border-zinc-200 dark:border-zinc-700">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 bg-zinc-100 dark:bg-zinc-700 rounded flex items-center justify-center"><File size={20} className="text-zinc-600 dark:text-zinc-300" /></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{file.name}</p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">{(file.size / 1024 / 1024).toFixed(2)} Mo {status && `• ${status}`}</p>
              </div>
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">{progress}%</span>
            </div>

            {[
              { label: 'Téléversement', threshold: 30 },
              { label: 'Extraction OCR / NLP', threshold: 65 },
              { label: 'Indexation en base', threshold: 100 },
            ].map((step) => (
              <div key={step.label} className="mb-4">
                <span className={progress >= step.threshold ? 'text-xs text-zinc-900 dark:text-zinc-100' : 'text-xs text-zinc-400 dark:text-zinc-500'}>{step.label}</span>
                <div className="w-full bg-zinc-100 dark:bg-zinc-700 rounded-full h-1 overflow-hidden mt-1"><div className="bg-zinc-900 dark:bg-zinc-100 h-full transition-all duration-300" style={{ width: `${progress >= step.threshold ? 100 : 0}%` }} /></div>
              </div>
            ))}

            {(progress === 100 || status === 'failed') && <button onClick={reset} className="w-full mt-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 text-sm font-medium py-2.5 rounded-md hover:bg-zinc-800 dark:hover:bg-zinc-300 transition-colors">Nouveau traitement</button>}
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
