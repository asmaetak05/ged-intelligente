import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PredictorML = () => {
  const [data, setData] = useState({ precision_svm: 0, anomalies_count: 0, anomalies_list: [] });

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/ml/anomalies')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8">
        <h2 className="text-xl font-medium text-zinc-900 mb-1">Modèles ML</h2>
        <p className="text-zinc-500 text-sm">Contrôle de cohérence par IA (Isolation Forest, SVM).</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-6 border border-zinc-200 rounded-md">
          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Anomalies Détectées</p>
          <p className="text-2xl font-light text-zinc-900">{data.anomalies_count}</p>
        </div>
        <div className="bg-white p-6 border border-zinc-200 rounded-md flex justify-between items-center">
          <div>
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Précision SVM</p>
            <p className="text-2xl font-light text-zinc-900">{data.precision_svm}%</p>
          </div>
          <button className="text-xs border border-zinc-200 px-3 py-1.5 rounded hover:bg-zinc-50">Réentraîner</button>
        </div>
      </div>

      <div className="bg-white flex-1 border border-zinc-200 rounded-md overflow-hidden">
        <div className="p-4 border-b border-zinc-200 bg-zinc-50/50">
          <h3 className="text-sm font-medium text-zinc-800">Watchlist de Classification</h3>
        </div>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-zinc-500 bg-white">
              <th className="p-4 font-medium">Référence</th>
              <th className="p-4 font-medium">Saisie (Humain)</th>
              <th className="p-4 font-medium">Prédiction (IA)</th>
              <th className="p-4 font-medium">Confiance</th>
              <th className="p-4 font-medium">Analyse</th>
            </tr>
          </thead>
          <tbody>
            {data.anomalies_list.map((a, i) => (
              <tr key={i} className="border-b border-zinc-100 hover:bg-zinc-50/50">
                <td className="p-4 text-zinc-900 font-mono text-xs">{a.id}</td>
                <td className="p-4">
                  <span className="px-2 py-0.5 rounded text-[11px] uppercase bg-zinc-100 text-zinc-600 line-through decoration-zinc-400">
                    {a.categorie}
                  </span>
                </td>
                <td className="p-4 font-medium text-zinc-900">{a.ai_pred}</td>
                <td className="p-4 text-zinc-500">{a.score}</td>
                <td className="p-4 text-zinc-500 text-xs">{a.raison}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PredictorML;
