import React, { useState } from 'react';
import { Users as UsersIcon, Search, MoreVertical, Edit2, Trash2, CheckCircle, XCircle } from 'lucide-react';

const MOCK_USERS = [
  { id: 1, name: 'Admin', email: 'admin@example.com', role: 'admin', active: true, lastLogin: '2026-07-19T10:30:00' },
  { id: 2, name: 'Jean Dupont', email: 'jean@example.com', role: 'user', active: true, lastLogin: '2026-07-18T14:20:00' },
  { id: 3, name: 'Marie Martin', email: 'marie@example.com', role: 'user', active: false, lastLogin: '2026-07-10T09:15:00' },
];

const Users = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredUsers = MOCK_USERS.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <UsersIcon className="w-6 h-6 mr-2" /> Gestion des Utilisateurs
        </h1>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition">
          + Nouvel Utilisateur
        </button>
      </div>
      
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <div className="relative w-72">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Rechercher un utilisateur..." 
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
                <th className="px-6 py-4">Utilisateur</th>
                <th className="px-6 py-4">Rôle</th>
                <th className="px-6 py-4">Statut</th>
                <th className="px-6 py-4">Dernière connexion</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.map(user => (
                <tr key={user.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-medium text-gray-900">{user.name}</span>
                      <span className="text-sm text-gray-500">{user.email}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                      ${user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {user.active ? (
                      <span className="inline-flex items-center text-sm text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" /> Actif
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-sm text-red-600">
                        <XCircle className="w-4 h-4 mr-1" /> Inactif
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(user.lastLogin).toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2 text-gray-400">
                      <button className="hover:text-blue-600 transition p-1"><Edit2 className="w-4 h-4" /></button>
                      <button className="hover:text-red-600 transition p-1"><Trash2 className="w-4 h-4" /></button>
                      <button className="hover:text-gray-600 transition p-1"><MoreVertical className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredUsers.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              Aucun utilisateur trouvé pour "{searchTerm}"
            </div>
          )}
        </div>
        
        <div className="p-4 border-t border-gray-200 bg-gray-50 text-sm text-gray-500 flex justify-between items-center">
          <span>Affichage de {filteredUsers.length} utilisateur(s)</span>
          <div className="flex gap-1">
            <button className="px-3 py-1 border border-gray-300 rounded-md bg-white text-gray-400 cursor-not-allowed">Précédent</button>
            <button className="px-3 py-1 border border-gray-300 rounded-md bg-white text-gray-400 cursor-not-allowed">Suivant</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Users;
