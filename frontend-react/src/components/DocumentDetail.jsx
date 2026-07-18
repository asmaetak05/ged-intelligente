import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, FileText, Download, Clock, CheckCircle } from 'lucide-react';

const DocumentDetail = () => {
  const { numero } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' or 'ocr'

  useEffect(() => {
    const fetchDoc = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:8000/api/v1/ged/appels-offres/${encodeURIComponent(numero)}`);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDoc();
  }, [numero]);

  if (loading) return <div className="p-8 text-zinc-500 text-sm">Chargement du document...</div>;
  if (!data) return <div className="p-8 text-zinc-500 text-sm">Document introuvable.</div>;

  const ocrLog = data.ocr_logs && data.ocr_logs.length > 0 ? data.ocr_logs[0] : null;

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <div className="mb-6 flex items-center gap-4">
        <Link to="/search" className="text-zinc-500 hover:text-zinc-900 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h2 className="text-xl font-medium text-zinc-900">{data.titre_projet || "Sans titre"}</h2>
          <p className="text-sm text-zinc-500">{data.organisme_acheteur} • AO n° {data.numero_appel_offre}</p>
        </div>
      </div>

      <div className="flex border-b border-zinc-200 mb-6">
        <button 
          className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'summary' ? 'border-zinc-900 text-zinc-900' : 'border-transparent text-zinc-500 hover:text-zinc-700'}`}
          onClick={() => setActiveTab('summary')}
        >
          Résumé & Métadonnées
        </button>
        <button 
          className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'ocr' ? 'border-zinc-900 text-zinc-900' : 'border-transparent text-zinc-500 hover:text-zinc-700'}`}
          onClick={() => setActiveTab('ocr')}
        >
          Texte Brut (OCR)
        </button>
      </div>

      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <div className="bg-white p-6 border border-zinc-200 rounded-md">
              <h3 className="text-sm font-medium text-zinc-800 mb-4">Informations Clés</h3>
              <div className="grid grid-cols-2 gap-y-4 text-sm">
                <div>
                  <p className="text-zinc-500 text-xs uppercase mb-1">Catégorie</p>
                  <p className="font-medium">{data.categorie_prestation || "N/A"}</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-xs uppercase mb-1">Montant Estimatif</p>
                  <p className="font-medium">{data.montant ? `${data.montant.toLocaleString()} MAD` : "Non spécifié"}</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-xs uppercase mb-1">Date de Parution</p>
                  <p className="font-medium">{data.date_parution || "N/A"}</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-xs uppercase mb-1">Ville d'exécution</p>
                  <p className="font-medium">{data.ville_execution || "Maroc"}</p>
                </div>
              </div>
            </div>

            {data.document && (
              <div className="bg-zinc-50 p-6 border border-zinc-200 rounded-md flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="text-zinc-400" />
                  <div>
                    <p className="text-sm font-medium text-zinc-900">Archive Originale</p>
                    <p className="text-xs text-zinc-500">{data.document.file_name}</p>
                  </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-white border border-zinc-200 rounded text-xs font-medium hover:bg-zinc-100 transition-colors">
                  <Download size={14} />
                  Télécharger
                </button>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="bg-white p-6 border border-zinc-200 rounded-md">
              <h3 className="text-sm font-medium text-zinc-800 mb-4">Qualité d'Extraction</h3>
              {ocrLog ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-zinc-500">Score de confiance</span>
                    <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                      <CheckCircle size={14} />
                      {ocrLog.confidence_score_avg}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-zinc-500">Moteur OCR</span>
                    <span className="text-sm text-zinc-900">{ocrLog.engine_name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-zinc-500">Temps de calcul</span>
                    <span className="text-sm text-zinc-900 flex items-center gap-1">
                      <Clock size={14} />
                      {ocrLog.processing_time_ms} ms
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-zinc-500">Aucune donnée OCR disponible.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'ocr' && (
        <div className="flex-1 bg-white border border-zinc-200 rounded-md p-6 overflow-y-auto">
          {ocrLog && ocrLog.raw_text_extracted ? (
            <pre className="text-xs font-mono text-zinc-700 whitespace-pre-wrap">
              {ocrLog.raw_text_extracted}
            </pre>
          ) : (
            <p className="text-sm text-zinc-500">Le texte brut n'a pas pu être extrait de ce document.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentDetail;
