import React from 'react';
import { Filter, X } from 'lucide-react';
 
const AdvancedFilters = ({ filters, setFilters, onReset, isOpen, setIsOpen }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };
 
  if (!isOpen) return null;
 
  return (
    <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md p-5 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
          <Filter size={14} /> Filtres Avancés
        </h3>
        <div className="flex gap-2">
          <button 
            type="button" 
            onClick={onReset}
            className="text-xs px-3 py-1.5 border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 rounded-md hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors"
          >
            Réinitialiser
          </button>
          <button 
            type="button" 
            onClick={() => setIsOpen(false)}
            className="text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300 p-1"
          >
            <X size={16} />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Type de procédure</label>
          <select 
            name="typeProcedure" 
            value={filters.typeProcedure || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          >
            <option value="">Tous les types</option>
            <option value="ouvert">Ouvert</option>
            <option value="restreint">Restreint</option>
          </select>
        </div>
 
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Statut de l'avis</label>
          <select 
            name="statutAvis" 
            value={filters.statutAvis || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          >
            <option value="">Tous les statuts</option>
            <option value="en cours">Avis en cours</option>
            <option value="résultats publiés">Résultats publiés</option>
            <option value="annulé">Annulé</option>
            <option value="clôturé">Clôturé</option>
          </select>
        </div>
 
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Date ouverture plis</label>
          <input 
            type="date" 
            name="dateOuverturePlis" 
            value={filters.dateOuverturePlis || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          />
        </div>
 
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Qualifications requises</label>
          <input 
            type="text" 
            name="qualifications" 
            placeholder="Ex: Qualif A..."
            value={filters.qualifications || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          />
        </div>
 
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Caution provisoire min (MAD)</label>
          <input 
            type="number" 
            name="cautionMin" 
            placeholder="Min..."
            value={filters.cautionMin || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          />
        </div>
 
        <div>
          <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1">Caution provisoire max (MAD)</label>
          <input 
            type="number" 
            name="cautionMax" 
            placeholder="Max..."
            value={filters.cautionMax || ''} 
            onChange={handleChange}
            className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
          />
        </div>
      </div>
    </div>
  );
};
 
export default AdvancedFilters;