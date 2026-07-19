import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900">
      <AlertCircle className="w-16 h-16 text-blue-500 mb-4" />
      <h1 className="text-4xl font-bold mb-2">404</h1>
      <p className="text-xl text-gray-600 mb-6">Page introuvable</p>
      <Link to="/" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Retour à l'accueil
      </Link>
    </div>
  );
};

export default NotFound;
