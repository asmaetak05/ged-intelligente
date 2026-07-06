import React from 'react';
import { Hammer } from 'lucide-react';

const Placeholder = ({ title }) => {
  return (
    <div className="h-full flex flex-col items-center justify-center text-slate-400 p-6">
      <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6">
        <Hammer size={48} className="text-slate-300" />
      </div>
      <h2 className="text-2xl font-bold text-slate-700 mb-2">{title}</h2>
      <p className="text-center max-w-md">
        Cet écran fait partie de la Phase 3 du PFA. Il sera connecté aux conteneurs Docker ou au microservice d'Intelligence Artificielle en production.
      </p>
    </div>
  );
};

export default Placeholder;
