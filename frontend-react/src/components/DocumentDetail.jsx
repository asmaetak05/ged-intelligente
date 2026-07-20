import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, MapPin, Banknote, Clock, ShieldCheck } from 'lucide-react';
 
const DocumentDetail = () => {
  const { numero } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
 
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
 
  if (loading) return <div className="p-8 text-zinc-500 dark:text-zinc-400 text-sm">Chargement du document...</div>;
  if (!data) return <div className="p-8 text-zinc-500 dark:text-zinc-400 text-sm">Document introuvable.</div>;
 
  const montant = data.estimation_mad ? Number(data.estimation_mad).toLocaleString('fr-FR') : null;
  const caution = data.caution_mad ? Number(data.caution_mad).toLocaleString('fr-FR') : null;
 
  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <div className="mb-6 flex items-center gap-4">
        <Link to="/search" className="text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100">{data.objet || "Sans titre"}</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{data.maitre_ouvrage} • AO n° {data.numero_ordre}</p>
        </div>
      </div>
 
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white dark:bg-zinc-800 p-6 border border-zinc-200 dark:border-zinc-700 rounded-md">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-4">Informations Clés</h3>
            <div className="grid grid-cols-2 gap-y-4 text-sm">
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Catégorie</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.categorie_marche || "N/A"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Montant Estimatif</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{montant ? `${montant} MAD` : "Non spécifié"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Lieu d'ouverture des plis</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.lieu_ouverture_plis || "N/A"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Région</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.region || "N/A"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Délai d'exécution</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.delai_execution || "N/A"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Pénalité de retard</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.penalite_retard || "N/A"}</p>
              </div>
            </div>
          </div>
 
          <div className="bg-white dark:bg-zinc-800 p-6 border border-zinc-200 dark:border-zinc-700 rounded-md">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-4 flex items-center gap-2">
              <ShieldCheck size={14} /> Caution
            </h3>
            <div className="grid grid-cols-2 gap-y-4 text-sm">
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Caution provisoire</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{caution ? `${caution} MAD` : "N/A"}</p>
              </div>
              <div>
                <p className="text-zinc-500 dark:text-zinc-400 text-xs uppercase mb-1">Caution définitive</p>
                <p className="font-medium text-zinc-900 dark:text-zinc-100">{data.caution_definitive || "N/A"}</p>
              </div>
            </div>
          </div>
        </div>
 
        <div className="space-y-6">
          <div className="bg-white dark:bg-zinc-800 p-6 border border-zinc-200 dark:border-zinc-700 rounded-md">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-4 flex items-center gap-2">
              <MapPin size={14} /> Localisation
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500 dark:text-zinc-400">Ville</span>
                <span className="text-sm text-zinc-900 dark:text-zinc-100">{data.lieu_ouverture_plis || "N/A"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500 dark:text-zinc-400">Région</span>
                <span className="text-sm text-zinc-900 dark:text-zinc-100">{data.region || "N/A"}</span>
              </div>
            </div>
          </div>
 
          <div className="bg-zinc-50 dark:bg-zinc-900/50 p-6 border border-zinc-200 dark:border-zinc-700 rounded-md">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-3 flex items-center gap-2">
              <Clock size={14} /> Ingestion
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              {data.date_ingestion ? new Date(data.date_ingestion).toLocaleString('fr-FR') : "N/A"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
 
export default DocumentDetail;
 