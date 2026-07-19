import React from 'react';
import useAuthStore from '../store/useAuthStore';
import { User, Mail, Settings, Shield } from 'lucide-react';

const Profile = () => {
  const { user } = useAuthStore();

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mon Profil</h1>
      
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200 bg-gray-50 flex items-center gap-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
            <User className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{user?.name || 'Utilisateur'}</h2>
            <p className="text-gray-500 capitalize">{user?.role || 'user'}</p>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom complet</label>
              <div className="flex items-center p-3 bg-gray-50 rounded-md border border-gray-200">
                <User className="w-5 h-5 text-gray-400 mr-3" />
                <span>{user?.name || 'Non défini'}</span>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Adresse Email</label>
              <div className="flex items-center p-3 bg-gray-50 rounded-md border border-gray-200">
                <Mail className="w-5 h-5 text-gray-400 mr-3" />
                <span>{user?.email || 'Non défini'}</span>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
              <div className="flex items-center p-3 bg-gray-50 rounded-md border border-gray-200">
                <Shield className="w-5 h-5 text-gray-400 mr-3" />
                <span className="capitalize">{user?.role || 'user'}</span>
              </div>
            </div>
          </div>
          
          <div className="pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" /> Préférences
            </h3>
            <p className="text-sm text-gray-500 italic">Les paramètres de préférences (langue, thème) seront bientôt disponibles.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
