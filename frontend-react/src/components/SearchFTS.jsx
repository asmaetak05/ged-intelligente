import React, { useState } from 'react';
import apiClient from '../api/axios';
import { Link } from 'react-router-dom';
import { Search, Filter, Download, FileSpreadsheet, ArrowUpDown, Sparkles, Building2, MapPin, Calendar, Coins } from 'lucide-react';
import AdvancedFilters from './AdvancedFilters';
import DOMPurify from 'dompurify';
import * as XLSX from 'xlsx';

const SearchFTS = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [sortBy, setSortBy] = useState('pertinence');
  const [orderDir, setOrderDir] = useState('desc');
  const [activeCategory, setActiveCategory] = useState('');
  
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const categories = [
    { id: '', label: 'Toutes catégories' },
    { id: 'Travaux', label: '🏗️ Travaux' },
    { id: 'Études', label: '📐 Études' },
    { id: 'Fournitures', label: '📦 Fournitures' },
    { id: 'Services', label: '🛠️ Services' },
  ];

  const appendFilters = (params, cat) => {
    if (cat) params.append('categorie', cat);
    ['region', 'ville', 'organisme'].forEach((key) => {
      if (filters[key]) params.append(key, filters[key]);
    });
    if (filters.dateMin) params.append('date_min', filters.dateMin);
    if (filters.dateMax) params.append('date_max', filters.dateMax);
    if (filters.montantMin) params.append('montant_min', filters.montantMin);
    if (filters.montantMax) params.append('montant_max', filters.montantMax);
  };

  const fetchResults = async (p = 1, cat = activeCategory) => {
    setIsLoading(true);
    setHasSearched(true);
    try {
      const params = new URLSearchParams({
        q: query,
        page: p,
        page_size: 10,
        order_by: sortBy,
        order_dir: orderDir,
      });

      appendFilters(params, cat);
      const hasTextQuery = query.trim().length > 0;
      const endpoint = hasTextQuery ? '/api/v1/ged/search' : '/api/v1/ged/appels-offres';
      const res = await apiClient.get(`${endpoint}?${params.toString()}`);
      setResults(hasTextQuery ? (res.data.results || []) : (res.data.items || []));
      setTotal(res.data.total || 0);
      setPage(p);
    } catch (error) {
      console.warn("FTS search fallback to general endpoint", error);
      try {
        const fallbackParams = new URLSearchParams({ q: query, page: p, page_size: 10 });
        appendFilters(fallbackParams, cat);
        const fallbackRes = await apiClient.get(`/api/v1/ged/appels-offres?${fallbackParams.toString()}`);
        setResults(fallbackRes.data.items || []);
        setTotal(fallbackRes.data.total || 0);
        setPage(p);
      } catch (err) {
        console.error("Search failed completely:", err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    fetchResults(1);
  };

  const handleCategoryClick = (catId) => {
    setActiveCategory(catId);
    fetchResults(1, catId);
  };

  const handleReset = () => {
    setQuery('');
    setFilters({});
    setActiveCategory('');
    setSortBy('pertinence');
    setOrderDir('desc');
    setResults([]);
    setHasSearched(false);
    setPage(1);
    setTotal(0);
  };

  const handleExportCSV = () => {
    if (!results || results.length === 0) return;
    const headers = ['Numéro', 'Objet', 'Organisme', 'Ville', 'Catégorie', 'Montant'];
    const csvRows = [headers.join(',')];
    
    results.forEach(res => {
      const values = [
        res.numero_appel_offre || res.numero_ordre || '',
        `"${(res.titre_projet || res.objet || '').replace(/"/g, '""')}"`,
        `"${(res.organisme_acheteur || res.maitre_ouvrage || '').replace(/"/g, '""')}"`,
        `"${(res.ville_execution || res.lieu_ouverture_plis || '').replace(/"/g, '""')}"`,
        `"${(res.categorie_prestation || res.categorie_marche || '').replace(/"/g, '""')}"`,
        res.montant || '',
      ];
      csvRows.push(values.join(','));
    });
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'marches_recherche.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportExcel = () => {
    if (!results || results.length === 0) return;
    const data = results.map(r => ({
      'Numéro': r.numero_appel_offre || r.numero_ordre,
      'Objet': r.titre_projet || r.objet,
      'Organisme': r.organisme_acheteur || r.maitre_ouvrage,
      'Ville': r.ville_execution || r.lieu_ouverture_plis,
      'Catégorie': r.categorie_prestation || r.categorie_marche,
      'Montant (MAD)': r.montant,
      'Score FTS': r.score ? `${(r.score * 100).toFixed(0)}%` : '-',
    }));
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Marchés");
    XLSX.writeFile(workbook, "marches_recherche.xlsx");
  };

  const renderHighlight = (res) => {
    if (res.highlight) {
      return (
        <p 
          className="text-xs text-zinc-700 dark:text-zinc-300 bg-amber-50 dark:bg-amber-950/30 p-3 rounded-lg border border-amber-200 dark:border-amber-900/50 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(res.highlight) }}
        />
      );
    }
    const text = res.titre_projet || res.objet || "Aucune description disponible";
    return <p className="text-xs text-zinc-600 dark:text-zinc-400">{text}</p>;
  };

  return (
    <div className="p-8 h-full flex flex-col max-w-7xl mx-auto w-full">
      {/* Header */}
      <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">
              Moteur de Recherche FTS
            </h2>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
              <Sparkles size={12} /> Full-Text Ranking
            </span>
          </div>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm mt-1">
            Indexation plein texte native PostgreSQL & extraction sémantique des marchés publics.
          </p>
        </div>
        
        {results.length > 0 && (
          <div className="flex items-center gap-2">
            <button 
              onClick={handleExportCSV}
              className="flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-200 text-xs font-medium rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-700/60 shadow-sm transition-all"
            >
              <Download size={14} /> CSV
            </button>
            <button 
              onClick={handleExportExcel}
              className="flex items-center gap-2 px-3.5 py-2 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs font-medium rounded-lg hover:bg-emerald-100/60 transition-all"
            >
              <FileSpreadsheet size={14} /> Excel
            </button>
          </div>
        )}
      </div>

      {/* Barre de recherche principale */}
      <div className="bg-white dark:bg-zinc-800/80 p-4 rounded-xl border border-zinc-200 dark:border-zinc-700/80 shadow-sm mb-6 space-y-3">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 text-zinc-400 dark:text-zinc-500" size={18} />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Rechercher par mots-clés : route, viaduc, barrage, surveillance météo, DGR..." 
              className="w-full pl-10 pr-4 py-2.5 bg-zinc-50 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 transition-all"
            />
          </div>
          
          <select 
            className="px-3.5 py-2.5 bg-zinc-50 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-700 rounded-lg text-sm text-zinc-800 dark:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="pertinence">Trier par : Pertinence</option>
            <option value="date_parution">Trier par : Date de parution</option>
            <option value="montant">Trier par : Montant estimé</option>
          </select>

          <button
            type="button"
            onClick={() => setOrderDir(orderDir === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2.5 bg-zinc-50 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-700 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300"
            title={orderDir === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}
          >
            <ArrowUpDown size={18} className={orderDir === 'asc' ? 'text-blue-600' : 'text-zinc-500'} />
          </button>

          <button 
            type="button" 
            onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            className={`px-4 py-2.5 border rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${isFiltersOpen ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950/40 dark:border-blue-800 dark:text-blue-300' : 'bg-zinc-50 dark:bg-zinc-900/80 border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100'}`}
          >
            <Filter size={16} /> Filtres
          </button>

          <button 
            type="submit" 
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-all flex items-center justify-center gap-2"
          >
            <Search size={16} /> Trouver
          </button>
        </form>

        {/* Pilules de catégories rapides */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-zinc-100 dark:border-zinc-700/40">
          {categories.map(c => (
            <button
              key={c.id}
              onClick={() => handleCategoryClick(c.id)}
              className={`px-3 py-1 text-xs rounded-full font-medium transition-all ${
                activeCategory === c.id 
                  ? 'bg-zinc-900 text-white dark:bg-white dark:text-zinc-900 shadow-sm' 
                  : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <AdvancedFilters 
        filters={filters} 
        setFilters={setFilters} 
        onReset={handleReset} 
        isOpen={isFiltersOpen} 
        setIsOpen={setIsFiltersOpen}
      />

      {/* Zone de résultats */}
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-zinc-500 dark:text-zinc-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
          Recherche plein texte en cours...
        </div>
      ) : hasSearched && results.length === 0 ? (
        <div className="bg-white dark:bg-zinc-800/60 p-8 rounded-xl border border-zinc-200 dark:border-zinc-700/80 text-center">
          <p className="text-zinc-700 dark:text-zinc-300 font-medium">Aucun résultat trouvé</p>
          <p className="text-zinc-500 text-sm mt-1">Essayez d'élargir vos termes ou de supprimer les filtres actifs.</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4">
          {results.length > 0 && (
            <div className="flex justify-between items-center px-1">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                {total} marché{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}
              </p>
              <span className="text-xs text-zinc-400">Page {page} / {Math.ceil(total / 10) || 1}</span>
            </div>
          )}

          {results.map((res, i) => {
            const docId = res.numero_appel_offre || res.numero_ordre;
            const category = res.categorie_prestation || res.categorie_marche || 'Non spécifié';
            const scorePct = res.score ? Math.round(res.score * 100) : null;

            return (
              <div 
                key={i} 
                className="bg-white dark:bg-zinc-800 border border-zinc-200/90 dark:border-zinc-700/80 rounded-xl p-5 hover:border-blue-400 dark:hover:border-blue-600 transition-all shadow-sm hover:shadow-md group"
              >
                <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-2 mb-2">
                  <Link 
                    to={`/document/${encodeURIComponent(docId)}`} 
                    className="text-base font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors"
                  >
                    {res.titre_projet || res.objet || `Marché N° ${res.numero_appel_offre || res.numero_ordre}`}
                  </Link>

                  <div className="flex items-center gap-2 shrink-0">
                    {scorePct !== null && (
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
                        Score {scorePct}%
                      </span>
                    )}
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-100 text-zinc-700 dark:bg-zinc-700 dark:text-zinc-300">
                      {category}
                    </span>
                  </div>
                </div>

                {/* Métadonnées */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400 mb-3">
                  <span className="font-mono font-medium text-zinc-700 dark:text-zinc-300">
                    {res.numero_appel_offre || res.numero_ordre}
                  </span>
                  {(res.organisme_acheteur || res.maitre_ouvrage) && (
                    <span className="flex items-center gap-1">
                      <Building2 size={13} className="text-zinc-400" />
                      {res.organisme_acheteur || res.maitre_ouvrage}
                    </span>
                  )}
                  {(res.ville_execution || res.lieu_ouverture_plis) && (
                    <span className="flex items-center gap-1">
                      <MapPin size={13} className="text-zinc-400" />
                      {res.ville_execution || res.lieu_ouverture_plis}
                    </span>
                  )}
                  {res.montant && (
                    <span className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400">
                      <Coins size={13} />
                      {Number(res.montant).toLocaleString('fr-FR')} MAD
                    </span>
                  )}
                  {res.date_parution && (
                    <span className="flex items-center gap-1">
                      <Calendar size={13} className="text-zinc-400" />
                      Paru le {res.date_parution}
                    </span>
                  )}
                </div>

                {/* Surlignage du contenu FTS */}
                {renderHighlight(res)}
              </div>
            );
          })}

          {/* Pagination */}
          {total > 10 && (
            <div className="flex justify-between items-center mt-6 pt-4 border-t border-zinc-200 dark:border-zinc-700">
              <button 
                onClick={() => fetchResults(page - 1)} 
                disabled={page === 1}
                className="px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 rounded-lg text-sm disabled:opacity-40 hover:bg-zinc-50 font-medium"
              >
                Précédent
              </button>
              <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">Page {page}</span>
              <button 
                onClick={() => fetchResults(page + 1)} 
                disabled={page * 10 >= total}
                className="px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 rounded-lg text-sm disabled:opacity-40 hover:bg-zinc-50 font-medium"
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
