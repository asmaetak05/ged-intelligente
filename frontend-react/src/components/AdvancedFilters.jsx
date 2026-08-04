import React from 'react';
import { Filter, X } from 'lucide-react';

const fields = [
  { name: 'region', label: 'Région', placeholder: 'Ex : Casablanca-Settat' },
  { name: 'ville', label: 'Ville', placeholder: 'Ex : Rabat' },
  { name: 'organisme', label: 'Organisme acheteur', placeholder: "Ex : Ministère de l’Équipement" },
  { name: 'dateMin', label: 'Date de parution à partir du', type: 'date' },
  { name: 'dateMax', label: "Date de parution jusqu’au", type: 'date' },
  { name: 'montantMin', label: 'Montant minimal (MAD)', type: 'number', placeholder: 'Min…' },
  { name: 'montantMax', label: 'Montant maximal (MAD)', type: 'number', placeholder: 'Max…' },
];

const AdvancedFilters = ({ filters, setFilters, onReset, isOpen, setIsOpen }) => {
  const handleChange = (event) => {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md p-5 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
          <Filter size={14} /> Filtres avancés
        </h3>
        <div className="flex gap-2">
          <button type="button" onClick={onReset} className="text-xs px-3 py-1.5 border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 rounded-md hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors">
            Réinitialiser
          </button>
          <button type="button" onClick={() => setIsOpen(false)} aria-label="Fermer les filtres" className="text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300 p-1">
            <X size={16} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {fields.map(({ name, label, type = 'text', placeholder }) => (
          <div key={name}>
            <label className="block text-xs text-zinc-500 dark:text-zinc-400 mb-1" htmlFor={`filter-${name}`}>{label}</label>
            <input
              id={`filter-${name}`}
              type={type}
              name={name}
              min={type === 'number' ? '0' : undefined}
              placeholder={placeholder}
              value={filters[name] || ''}
              onChange={handleChange}
              className="w-full px-3 py-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 rounded text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdvancedFilters;
