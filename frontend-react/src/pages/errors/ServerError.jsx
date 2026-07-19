import React from 'react';
import { Link } from 'react-router-dom';
import { ServerCrash } from 'lucide-react';

const ServerError = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
      <ServerCrash className="w-16 h-16 text-orange-500 mb-4" />
      <h1 className="text-4xl font-bold mb-2">500</h1>
      <p className="text-xl text-gray-600 mb-6">Erreur serveur interne</p>
      <Link to="/" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Retour à l'accueil
      </Link>
    </div>
  );
};

export default ServerError;
