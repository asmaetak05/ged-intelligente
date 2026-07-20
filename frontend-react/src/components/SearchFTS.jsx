import React, { useState } from 'react';
import apiClient from '../api/axios';
import { Link } from 'react-router-dom';
import { Search, Filter, Download, FileSpreadsheet, ArrowUpDown } from 'lucide-react';
import AdvancedFilters from './AdvancedFilters';
import DOMPurify from 'dompurify';
import * as XLSX from 'xlsx';
 
const SearchFTS = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [sortBy, setSortBy] = useState('pertinence');
  const [orderDir, setOrderDir] = useState('desc');
  
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
 
  const buildQueryString = (p) => {
    const params = new URLSearchParams({
      q: query,
      page: p,
      page_size: 10
    });
    
    if (filters.typeProcedure) params.append('type_procedure', filters.typeProcedure);
    if (filters.statutAvis) params.append('statut_avis', filters.statutAvis);
    if (filters.dateOuverturePlis) params.append('date_ouverture_plis', filters.dateOuverturePlis);
    if (filters.qualifications) params.append('qualifications', filters.qualifications);
    if (filters.cautionMin) params.append('caution_min', filters.cautionMin);
    if (filters.cautionMax) params.append('caution_max', filters.cautionMax);
    
    if (sortBy && sortBy !== 'pertinence') params.append('sort_by', sortBy);
    if (orderDir) params.append('order_dir', orderDir);
    
    return params.toString();
  };
 
  const fetchResults = async (p = 1) => {
    setIsLoading(true);
    setHasSearched(true);
    try {
      const res = await apiClient.get(`/api/v1/ged/appels-offres?${buildQueryString(p)}`);
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
    if (e) e.preventDefault();
    fetchResults(1);
  };
 
  const handleReset = () => {
    setQuery('');
    setFilters({});
    setSortBy('pertinence');
    setOrderDir('desc');
    setResults([]);
    setHasSearched(false);
    setPage(1);
    setTotal(0);
  };
 
  const handleExportCSV = () => {
    if (!results || results.length === 0) return;
    
    const headers = ['Numéro', 'Objet', 'Maître d\'ouvrage', 'Lieu', 'Catégorie'];
    const csvRows = [headers.join(',')];
    
    results.forEach(res => {
      const values = [
        res.numero_ordre || '',
        `"${(res.objet || '').replace(/"/g, '""')}"`,
        `"${(res.maitre_ouvrage || '').replace(/"/g, '""')}"`,
        `"${(res.lieu_ouverture_plis || '').replace(/"/g, '""')}"`,
        `"${(res.categorie_marche || '').replace(/"/g, '""')}"`
      ];
      csvRows.push(values.join(','));
    });
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'resultats_recherche.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
 
  const handleExportExcel = () => {
    if (!results || results.length === 0) return;
    
    const data = results.map(r => ({
      'Numéro': r.numero_ordre,
      'Objet': r.objet,
      'Maître d\'ouvrage': r.maitre_ouvrage,
      'Lieu': r.lieu_ouverture_plis,
      'Catégorie': r.categorie_marche,
    }));
    
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Résultats");
    XLSX.writeFile(workbook, "resultats_recherche.xlsx");
  };
 
  const highlightSnippet = (text) => {
    if (!text || !query) return text;
    // VERY simple regex highlighting for demonstration
    const regex = new RegExp(`(${query.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
    const highlighted = text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-500/40 text-black dark:text-zinc-100">$1</mark>');
    return <span dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(highlighted) }} />;
  };
 
  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100 mb-1">Recherche Sémantique</h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm">PostgreSQL Full Text Search engine.</p>
        </div>
        {results.length > 0 && (
          <div className="flex gap-2">
            <button 
              onClick={handleExportCSV}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-200 text-sm font-medium rounded-md hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors"
            >
              <Download size={16} /> CSV
            </button>
            <button 
              onClick={handleExportExcel}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-zinc-800 border border-green-200 dark:border-green-700 text-green-700 dark:text-green-400 text-sm font-medium rounded-md hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors"
            >
              <FileSpreadsheet size={16} /> Excel
            </button>
          </div>
        )}
      </div>
 
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 text-zinc-400 dark:text-zinc-500" size={16} />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: Élargissement RR507..." 
              className="w-full pl-9 pr-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500 text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 transition-colors"
            />
          </div>
          
          <select 
            className="px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm text-zinc-900 dark:text-zinc-100 focus:outline-none"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="pertinence">Pertinence</option>
            <option value="date_publication">Date de publication</option>
            <option value="estimation_mad">Montant estimé</option>
          </select>
 
          <button
            type="button"
            onClick={() => setOrderDir(orderDir === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md hover:bg-zinc-50 dark:hover:bg-zinc-700"
            title="Trier asc/desc"
          >
            <ArrowUpDown size={16} className={orderDir === 'asc' ? 'text-blue-500 dark:text-blue-400' : 'text-zinc-500 dark:text-zinc-400'} />
          </button>
 
          <button 
            type="button" 
            onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            className={`px-4 py-2 border rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${isFiltersOpen ? 'bg-zinc-100 dark:bg-zinc-700 border-zinc-300 dark:border-zinc-600 text-zinc-800 dark:text-zinc-100' : 'bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700'}`}
          >
            <Filter size={16} /> Filtres
          </button>
          <button type="submit" className="px-6 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 text-sm font-medium rounded-md hover:bg-zinc-800 dark:hover:bg-zinc-300 transition-colors">
            Rechercher
          </button>
        </form>
      </div>
 
      <AdvancedFilters 
        filters={filters} 
        setFilters={setFilters} 
        onReset={handleReset} 
        isOpen={isFiltersOpen} 
        setIsOpen={setIsFiltersOpen}
      />
 
      {isLoading ? (
        <div className="text-sm text-zinc-500 dark:text-zinc-400">Recherche en cours...</div>
      ) : hasSearched && results.length === 0 ? (
        <div className="text-sm text-zinc-500 dark:text-zinc-400">Aucun résultat trouvé pour "{query}".</div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4">
          {results.length > 0 && <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">{results.length} résultats</p>}
          {results.map((res, i) => (
            <div key={i} className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md p-5 group">
              <div className="flex justify-between items-start mb-1">
                <Link to={`/document/${encodeURIComponent(res.numero_ordre)}`} className="text-sm font-medium text-zinc-900 dark:text-zinc-100 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors">
                  {res.objet ? highlightSnippet(res.objet) : highlightSnippet(`Appel d'offres n°${res.numero_ordre}`)}
                </Link>
                <span className="text-[10px] uppercase tracking-wider border border-zinc-200 dark:border-zinc-700 px-2 py-0.5 rounded text-zinc-500 dark:text-zinc-400">{res.categorie_marche}</span>
              </div>
              <div className="flex gap-3 text-xs text-zinc-500 dark:text-zinc-400 mb-4">
                <span>{res.numero_ordre}</span>
                <span>•</span>
                <span>{res.maitre_ouvrage}</span>
                <span>•</span>
                <span>{res.lieu_ouverture_plis}</span>
              </div>
              <p className="text-sm text-zinc-600 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-900/50 p-3 rounded-md border border-zinc-100 dark:border-zinc-700 font-serif mt-4">
                {res.objet ? "Résultat sémantique pertinent avec la requête." : "Contenu de l'appel d'offres correspond à votre recherche."}
              </p>
            </div>
          ))}
          
          {total > 10 && (
            <div className="flex justify-between items-center mt-6 pt-4 border-t border-zinc-200 dark:border-zinc-700">
              <button 
                onClick={() => fetchResults(page - 1)} 
                disabled={page === 1}
                className="px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded text-sm disabled:opacity-50"
              >
                Précédent
              </button>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">Page {page}</span>
              <button 
                onClick={() => fetchResults(page + 1)} 
                disabled={page * 10 >= total}
                className="px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 rounded text-sm disabled:opacity-50"
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