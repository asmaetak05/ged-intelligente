import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../api/axios';

const PredictorML = () => {
  const [data, setData] = useState({ anomalies_count: 0, anomalies_list: [] });
  const [accuracy, setAccuracy] = useState(null);
  const [isRetraining, setIsRetraining] = useState(false);

  const loadData = async () => {
    try {
      const [anomalies, metrics] = await Promise.all([
        apiClient.get('/api/v1/ml/anomalies'),
        apiClient.get('/api/v1/ml/metrics'),
      ]);
      setData(anomalies.data);
      setAccuracy(metrics.data.accuracy ?? null);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => { loadData(); }, []);

  const retrain = async () => {
    setIsRetraining(true);
    try {
      const response = await apiClient.post('/api/v1/ml/retrain');
      toast.success(response.data.message || 'Réentraînement lancé.');
      window.setTimeout(loadData, 1500);
    } catch (error) {
      console.error(error);
    } finally {
      setIsRetraining(false);
    }
  };

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8"><h2 className="text-xl font-medium text-zinc-900 mb-1">Modèles ML</h2><p className="text-zinc-500 text-sm">Contrôle de cohérence par IA et détection d’anomalies.</p></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-6 border border-zinc-200 rounded-md"><p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Anomalies détectées</p><p className="text-2xl font-light text-zinc-900">{data.anomalies_count}</p></div>
        <div className="bg-white p-6 border border-zinc-200 rounded-md flex justify-between items-center"><div><p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Précision du classifieur</p><p className="text-2xl font-light text-zinc-900">{accuracy === null ? '—' : `${(accuracy * 100).toFixed(1)}%`}</p></div><button onClick={retrain} disabled={isRetraining} className="text-xs border border-zinc-200 px-3 py-1.5 rounded hover:bg-zinc-50 disabled:opacity-50">{isRetraining ? 'Lancement…' : 'Réentraîner'}</button></div>
      </div>
      <div className="bg-white flex-1 border border-zinc-200 rounded-md overflow-hidden"><div className="p-4 border-b border-zinc-200 bg-zinc-50/50"><h3 className="text-sm font-medium text-zinc-800">Watchlist de classification</h3></div><table className="w-full text-left text-sm"><thead><tr className="border-b border-zinc-200 text-zinc-500 bg-white"><th className="p-4 font-medium">Référence</th><th className="p-4 font-medium">Catégorie déclarée</th><th className="p-4 font-medium">Prédiction IA</th><th className="p-4 font-medium">Confiance</th><th className="p-4 font-medium">Score anomalie</th></tr></thead><tbody>{data.anomalies_list.map((item) => <tr key={item.marche_id} className="border-b border-zinc-100 hover:bg-zinc-50/50"><td className="p-4 text-zinc-900 font-mono text-xs">{item.numero_appel_offre || item.marche_id}</td><td className="p-4">{item.categorie || 'Non renseignée'}</td><td className="p-4 font-medium text-zinc-900">{item.predicted_categorie || 'Non disponible'}</td><td className="p-4 text-zinc-500">{item.classification_confidence === null ? '—' : `${(item.classification_confidence * 100).toFixed(0)}%`}</td><td className="p-4 text-zinc-500">{(item.anomaly_score * 100).toFixed(0)}%</td></tr>)}</tbody></table>{data.anomalies_list.length === 0 && <p className="p-8 text-center text-sm text-zinc-500">Aucune anomalie détectée.</p>}</div>
    </div>
  );
};

export default PredictorML;
