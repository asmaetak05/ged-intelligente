import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';

const SearchFTS = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchResults = async (p = 1) => {
    setIsLoading(true);
    setHasSearched(true);
    try {
      // Utilisation de l'endpoint d'appels-offres qui gère le FTS `q=` et la pagination
      const res = await axios.get(`http://127.0.0.1:8000/api/v1/ged/appels-offres?q=${query}&page=${p}&page_size=10`);
      setResults(res.data.items);
      setTotal(res.data.total);
      setPage(p);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchResults(1);
  };

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8">
        <h2 className="text-xl font-medium text-zinc-900 mb-1">Recherche Sémantique</h2>
        <p className="text-zinc-500 text-sm">PostgreSQL Full Text Search engine.</p>
      </div>

      <div className="mb-8">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 text-zinc-400" size={16} />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: Élargissement RR507..." 
              className="w-full pl-9 pr-4 py-2 bg-white border border-zinc-200 rounded-md focus:outline-none focus:border-zinc-400 text-sm transition-colors"
            />
          </div>
          <button type="submit" className="px-6 py-2 bg-zinc-900 text-white text-sm font-medium rounded-md hover:bg-zinc-800 transition-colors">
            Rechercher
          </button>
        </form>
      </div>

      {isLoading ? (
        <div className="text-sm text-zinc-500">Recherche en cours...</div>
      ) : hasSearched && results.length === 0 ? (
        <div className="text-sm text-zinc-500">Aucun résultat trouvé pour "{query}".</div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4">
          {results.length > 0 && <p className="text-xs text-zinc-500 uppercase tracking-wider">{results.length} résultats</p>}
          {results.map((res, i) => (
            <div key={i} className="bg-white border border-zinc-200 rounded-md p-5 group">
              <div className="flex justify-between items-start mb-1">
                <Link to={`/document/${res.numero_appel_offre}`} className="text-sm font-medium text-zinc-900 group-hover:text-zinc-600 transition-colors">
                  {res.titre_projet || `Appel d'offres n°${res.numero_appel_offre}`}
                </Link>
                <span className="text-[10px] uppercase tracking-wider border border-zinc-200 px-2 py-0.5 rounded text-zinc-500">{res.categorie_prestation}</span>
              </div>
              <div className="flex gap-3 text-xs text-zinc-500 mb-4">
                <span>{res.numero_appel_offre}</span>
                <span>•</span>
                <span>{res.organisme_acheteur}</span>
                <span>•</span>
                <span>{res.ville_execution}</span>
              </div>
              <p className="text-sm text-zinc-600 bg-zinc-50 p-3 rounded-md border border-zinc-100 font-serif mt-4">
                {res.titre_projet ? "Résultat sémantique pertinent avec la requête." : "Contenu de l'appel d'offres correspond à votre recherche."}
              </p>
            </div>
          ))}
          
          {total > 10 && (
            <div className="flex justify-between items-center mt-6 pt-4 border-t border-zinc-200">
              <button 
                onClick={() => fetchResults(page - 1)} 
                disabled={page === 1}
                className="px-4 py-2 bg-white border border-zinc-200 rounded text-sm disabled:opacity-50"
              >
                Précédent
              </button>
              <span className="text-sm text-zinc-500">Page {page}</span>
              <button 
                onClick={() => fetchResults(page + 1)} 
                disabled={page * 10 >= total}
                className="px-4 py-2 bg-white border border-zinc-200 rounded text-sm disabled:opacity-50"
              >
                Suivant
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchFTS;
