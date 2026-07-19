import React, { useState } from 'react';
import { Activity, Search, Filter, Clock, User, FileText } from 'lucide-react';

const MOCK_AUDITS = [
  { id: 1, action: 'Connexion', user: 'admin@example.com', ip: '192.168.1.1', date: '2026-07-19T10:30:00', details: 'Connexion réussie', type: 'auth' },
  { id: 2, action: 'Export CSV', user: 'jean@example.com', ip: '192.168.1.42', date: '2026-07-18T14:25:00', details: 'Export de 150 appels d\'offres', type: 'data' },
  { id: 3, action: 'Modification Utilisateur', user: 'admin@example.com', ip: '192.168.1.1', date: '2026-07-18T09:15:00', details: 'Désactivation de marie@example.com', type: 'admin' },
  { id: 4, action: 'Upload Document', user: 'jean@example.com', ip: '192.168.1.42', date: '2026-07-17T16:40:00', details: 'Upload de CPS_Marche_Public.pdf', type: 'data' },
];

const Audit = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredAudits = MOCK_AUDITS.filter(audit => 
    audit.action.toLowerCase().includes(searchTerm.toLowerCase()) || 
    audit.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
    audit.details.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getActionIcon = (type) => {
    switch(type) {
      case 'auth': return <Activity className="w-5 h-5 text-blue-500" />;
      case 'admin': return <User className="w-5 h-5 text-purple-500" />;
      case 'data': return <FileText className="w-5 h-5 text-green-500" />;
      default: return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Activity className="w-6 h-6 mr-2" /> Audit & Traçabilité
        </h1>
        <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition flex items-center">
          <Filter className="w-4 h-4 mr-2" /> Filtrer
        </button>
      </div>
      
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <div className="relative w-96">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Rechercher une action, un utilisateur..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-xs uppercase text-gray-500 font-semibold tracking-wider">
                <th className="px-6 py-4 w-12"></th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Utilisateur</th>
                <th className="px-6 py-4">Adresse IP</th>
                <th className="px-6 py-4">Détails</th>
                <th className="px-6 py-4 text-right">Date et Heure</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredAudits.map(audit => (
                <tr key={audit.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4">
                    {getActionIcon(audit.type)}
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {audit.action}
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {audit.user}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 font-mono">
                    {audit.ip}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {audit.details}
                  </td>
                  <td className="px-6 py-4 text-right text-sm text-gray-500">
                    {new Date(audit.date).toLocaleString('fr-FR')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredAudits.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              Aucune action trouvée pour "{searchTerm}"
            </div>
          )}
        </div>
        
        <div className="p-4 border-t border-gray-200 bg-gray-50 text-sm text-gray-500 flex justify-between items-center">
          <span>Affichage de {filteredAudits.length} événement(s)</span>
          <div className="flex gap-1">
            <button className="px-3 py-1 border border-gray-300 rounded-md bg-white text-gray-400 cursor-not-allowed">Précédent</button>
            <button className="px-3 py-1 border border-gray-300 rounded-md bg-white text-gray-400 cursor-not-allowed">Suivant</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Audit;
