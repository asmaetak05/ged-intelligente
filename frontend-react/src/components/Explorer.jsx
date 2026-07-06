import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { File, FolderArchive } from 'lucide-react';

const Explorer = () => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/ged/documents')
      .then(res => setDocuments(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8">
        <h2 className="text-xl font-medium text-zinc-900 mb-1">Explorateur</h2>
        <p className="text-zinc-500 text-sm">Gestionnaire de fichiers et suivi des statuts d'ingestion.</p>
      </div>

      <div className="bg-white border border-zinc-200 rounded-md flex-1 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-zinc-500 bg-zinc-50/50">
              <th className="p-4 font-medium">Nom</th>
              <th className="p-4 font-medium">Type</th>
              <th className="p-4 font-medium">Taille</th>
              <th className="p-4 font-medium">Date</th>
              <th className="p-4 font-medium">Statut</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc, idx) => (
              <tr key={idx} className="border-b border-zinc-100 hover:bg-zinc-50/50 transition-colors">
                <td className="p-4 flex items-center gap-3 text-zinc-800">
                  {doc.type === "Archive" ? <FolderArchive size={16} className="text-zinc-400" /> : <File size={16} className="text-zinc-400" />}
                  {doc.name}
                </td>
                <td className="p-4 text-zinc-500">{doc.type}</td>
                <td className="p-4 text-zinc-500">{doc.size}</td>
                <td className="p-4 text-zinc-500">{doc.date}</td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded text-[11px] uppercase tracking-wide ${
                    doc.status === 'Échec' ? 'bg-red-50 text-red-600 border border-red-100' :
                    doc.status === 'En cours' ? 'bg-amber-50 text-amber-600 border border-amber-100' :
                    'bg-zinc-100 text-zinc-600 border border-zinc-200'
                  }`}>
                    {doc.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Explorer;
