import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Monitoring = () => {
  const [data, setData] = useState({ api_uptime: "...", api_status: "...", db_index: "...", db_status: "...", logs: [] });

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/system/monitoring')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8">
        <h2 className="text-xl font-medium text-zinc-900 mb-1">Monitoring</h2>
        <p className="text-zinc-500 text-sm">Supervision de l'infrastructure.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-5 border border-zinc-200 rounded-md flex justify-between items-start">
          <div>
            <h3 className="text-sm font-medium text-zinc-900 mb-1">API Backend (FastAPI)</h3>
            <p className="text-xs text-zinc-500">Uptime: {data.api_uptime}</p>
          </div>
          <span className={`flex h-2 w-2 rounded-full ${data.api_status === 'Online' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
        </div>

        <div className="bg-white p-5 border border-zinc-200 rounded-md flex justify-between items-start">
          <div>
            <h3 className="text-sm font-medium text-zinc-900 mb-1">Base de Données (PostgreSQL)</h3>
            <p className="text-xs text-zinc-500">Index GIN: {data.db_index}</p>
          </div>
          <span className={`flex h-2 w-2 rounded-full ${data.db_status === 'Connecté' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
        </div>
      </div>

      <div className="bg-[#111111] rounded-md p-6 font-mono text-xs flex-1 flex flex-col border border-zinc-800 shadow-inner">
        <div className="text-zinc-500 mb-4 pb-2 border-b border-zinc-800">
          ~ tail -f /var/log/extraction.log
        </div>
        <div className="space-y-1.5 flex-1 overflow-y-auto text-zinc-400">
          {data.logs.map((log, i) => (
            <p key={i}>
              <span className={log.level === 'WARN' ? 'text-yellow-500/80' : log.level === 'SUCC' ? 'text-emerald-500/80' : 'text-zinc-600'}>
                [{log.time}] {log.level}:
              </span> {log.msg}
            </p>
          ))}
          <p className="animate-pulse text-zinc-500">_</p>
        </div>
      </div>
    </div>
  );
};

export default Monitoring;
