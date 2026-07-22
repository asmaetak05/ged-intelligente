import React, { useState, useEffect, useRef } from 'react';
import { Play, Database, FileText, UploadCloud, Server } from 'lucide-react';
import useAuthStore from '../store/useAuthStore';


const PipelineAdmin = () => {
  const [logs, setLogs] = useState([]);
  const [schema, setSchema] = useState([]);
  const [dates, setDates] = useState({ start: '01/01/2025', end: '31/12/2025' });
  const ws = useRef(null);
  const consoleRef = useRef(null);

  useEffect(() => {
    // Fetch schema
    fetch('http://localhost:8000/api/v1/system/schema')
      .then(res => res.json())
      .then(data => setSchema(data))
      .catch(err => console.error(err));

    // Setup WebSocket — avec le token JWT dans l'URL
    const token = useAuthStore.getState().token;
    if (!token) {
      setLogs(prev => [...prev, "Erreur : vous devez être connecté (rôle admin) pour utiliser la console."]);
      return;
    }

    ws.current = new WebSocket(`ws://localhost:8000/api/v1/system/ws/console?token=${token}`);
    ws.current.onmessage = (event) => {
      setLogs(prev => [...prev, event.data]);
    };
    ws.current.onerror = () => {
      setLogs(prev => [...prev, "Erreur de connexion WebSocket (vérifiez que vous êtes bien admin)."]);
    };
    ws.current.onclose = (event) => {
      if (event.code === 1008) {
        setLogs(prev => [...prev, "Connexion refusée : token invalide ou rôle insuffisant (admin requis)."]);
      }
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  const sendCommand = (action) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      setLogs(prev => [...prev, `> Execution: ${action}...`]);
      ws.current.send(JSON.stringify({ 
        action, 
        date_debut: dates.start, 
        date_fin: dates.end 
      }));
    }
  };

  return (
    <div className="p-8 h-full flex flex-col gap-6">
      <div className="flex items-center gap-2 pb-4 border-b border-zinc-200 dark:border-zinc-700">
        <Server className="text-zinc-900 dark:text-zinc-100" />
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100 tracking-tight">Pipeline & Admin</h1>
      </div>

      <div className="flex flex-1 gap-6 min-h-0">
        {/* Left Column: Controls & Schema */}
        <div className="w-1/2 flex flex-col gap-6 overflow-y-auto pr-2">
          
          {/* Controls */}
          <div className="bg-white dark:bg-zinc-800 p-5 rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm">
            <h2 className="text-lg font-medium mb-4 text-zinc-900 dark:text-zinc-100">Contrôleur de Pipeline</h2>
            
            <div className="flex gap-4 mb-6">
              <div className="flex-1">
                <label className="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">Date de début (Scraping)</label>
                <input 
                  type="text" 
                  value={dates.start}
                  onChange={(e) => setDates({...dates, start: e.target.value})}
                  className="w-full border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-zinc-500 dark:focus:border-zinc-400" 
                  placeholder="JJ/MM/AAAA"
                />
              </div>
              <div className="flex-1">
                <label className="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">Date de fin (Scraping)</label>
                <input 
                  type="text" 
                  value={dates.end}
                  onChange={(e) => setDates({...dates, end: e.target.value})}
                  className="w-full border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-zinc-500 dark:focus:border-zinc-400" 
                  placeholder="JJ/MM/AAAA"
                />
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <button 
                onClick={() => sendCommand('scrape')}
                className="flex items-center justify-center gap-2 w-full bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-300 text-white dark:text-zinc-900 py-2.5 rounded-md text-sm font-medium transition-colors">
                <Play size={16} /> Lancer le Scraping (Téléchargement)
              </button>
              <button 
                onClick={() => sendCommand('extract')}
                className="flex items-center justify-center gap-2 w-full bg-white dark:bg-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-700 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-200 py-2.5 rounded-md text-sm font-medium transition-colors">
                <FileText size={16} /> Extraire les Données (OCR/NLP)
              </button>
              <button 
                onClick={() => sendCommand('ingest')}
                className="flex items-center justify-center gap-2 w-full bg-white dark:bg-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-700 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-200 py-2.5 rounded-md text-sm font-medium transition-colors">
                <Database size={16} /> Ingestion en Base de Données
              </button>
            </div>
          </div>

          {/* Schema Viewer */}
          <div className="bg-white dark:bg-zinc-800 p-5 rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm flex-1">
            <h2 className="text-lg font-medium mb-4 text-zinc-900 dark:text-zinc-100">Schéma de la Base</h2>
            <div className="space-y-4">
              {schema.map((table, idx) => (
                <div key={idx} className="border border-zinc-100 dark:border-zinc-700 rounded-lg overflow-hidden">
                  <div className="bg-zinc-50 dark:bg-zinc-900/50 px-3 py-2 border-b border-zinc-100 dark:border-zinc-700 font-medium text-sm text-zinc-800 dark:text-zinc-200 flex justify-between">
                    <span>{table.table}</span>
                    <span className="text-xs text-zinc-500 dark:text-zinc-400">{table.columns.length} cols</span>
                  </div>
                  <div className="p-3 text-xs bg-white dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 max-h-40 overflow-y-auto">
                    <ul className="space-y-1">
                      {table.columns.map((col, cidx) => (
                        <li key={cidx} className="flex justify-between">
                          <span className={col.primary_key ? 'font-bold text-zinc-900 dark:text-zinc-100' : ''}>{col.name}</span>
                          <span className="text-zinc-400 dark:text-zinc-500 font-mono">{col.type}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Console — reste sombre volontairement (style terminal) */}
        <div className="w-1/2 bg-[#0a0a0a] rounded-xl shadow-lg border border-zinc-800 flex flex-col overflow-hidden h-full">
          <div className="bg-[#1a1a1a] px-4 py-2 border-b border-zinc-800 flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="ml-2 text-xs font-mono text-zinc-400">Terminal (Temps réel)</span>
          </div>
          <div 
            ref={consoleRef}
            className="flex-1 p-4 font-mono text-xs text-green-400 overflow-y-auto whitespace-pre-wrap leading-relaxed break-all"
          >
            {logs.map((log, idx) => (
              <div key={idx}>{log}</div>
            ))}
            {logs.length === 0 && <span className="text-zinc-600">En attente de commandes...</span>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineAdmin;