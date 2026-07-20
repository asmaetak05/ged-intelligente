import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BarChart3, BrainCircuit, Search, ScanText, ShieldCheck, MapPin, Building2, Briefcase } from 'lucide-react';
import logo from '../assets/logo.jpg';
import texture from '../assets/texture.jpg';
 
const LandingPage = () => {
  const navigate = useNavigate();
 
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 font-sans selection:bg-emerald-500 selection:text-white relative">
      {/* Texture Background */}
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: `url(${texture})`, backgroundSize: 'cover', backgroundPosition: 'center', opacity: 0.07 }}></div>
      
      {/* Header */}
      <header className="relative z-10 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-700 sticky top-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src={logo} alt="Royaume du Maroc - Ministère de l'Equipement" className="h-12 object-contain" />
            <div className="h-8 w-px bg-zinc-300 dark:bg-zinc-600 mx-2"></div>
            <div>
              <h1 className="text-lg font-bold text-emerald-900 dark:text-emerald-300 leading-tight">GED Intelligente</h1>
              <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400 tracking-wider uppercase">Plateforme Décisionnelle</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/pipeline')}
              className="text-sm font-medium text-zinc-600 dark:text-zinc-300 hover:text-emerald-700 dark:hover:text-emerald-400 transition-colors"
            >
              Pipeline Admin
            </button>
            <button 
              onClick={() => navigate('/dashboard')}
              className="bg-emerald-700 hover:bg-emerald-800 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-all shadow-sm shadow-emerald-900/20 flex items-center gap-2"
            >
              Accéder au Dashboard <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </header>
 
      {/* Hero Section */}
      <section className="relative z-10 pt-24 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-100/50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold mb-8 tracking-wide uppercase shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Système de Gestion des Marchés Publics V2.0
          </div>
          <h2 className="text-5xl md:text-6xl font-extrabold text-zinc-900 dark:text-zinc-100 tracking-tight leading-[1.1] mb-6">
            La donnée des appels d'offres, <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-700 to-teal-500">décryptée par l'Intelligence Artificielle.</span>
          </h2>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            Centralisez, analysez et précevez les tendances des marchés publics. 
            Grâce à la combinaison de l'OCR et du Machine Learning, transformez les archives brutes en tableaux de bord stratégiques et alertes instantanées.
          </p>
          
          {/* Mockup Preview */}
          <div className="relative mx-auto max-w-4xl rounded-2xl border border-zinc-200/80 dark:border-zinc-700/80 bg-white/50 dark:bg-zinc-800/50 backdrop-blur-sm p-2 shadow-2xl shadow-zinc-200/50 dark:shadow-black/50 mt-12 overflow-hidden transform transition-transform hover:scale-[1.01] duration-500">
            <div className="absolute inset-0 bg-gradient-to-t from-zinc-50 dark:from-zinc-900 to-transparent z-10 pointer-events-none"></div>
            <img 
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80" 
              alt="Dashboard BI Preview" 
              className="w-full h-64 object-cover rounded-xl opacity-60 grayscale-[30%]"
            />
            <div className="absolute bottom-8 left-0 right-0 z-20 flex justify-center">
              <button 
                onClick={() => navigate('/dashboard')}
                className="bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-300 text-white dark:text-zinc-900 px-8 py-3.5 rounded-full text-base font-medium transition-all shadow-xl shadow-zinc-900/20 flex items-center gap-2 hover:-translate-y-0.5"
              >
                Explorer la base de données <Search size={18} />
              </button>
            </div>
          </div>
        </div>
      </section>
 
      {/* Data Overview Section */}
      <section className="relative z-10 py-20 bg-white dark:bg-zinc-900 border-y border-zinc-100 dark:border-zinc-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">Une couverture exhaustive du territoire</h3>
            <p className="text-zinc-500 dark:text-zinc-400 max-w-2xl mx-auto">Notre moteur de collecte scrute le portail officiel pour récupérer l'intégralité de la donnée économique.</p>
          </div>
 
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Organismes */}
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-2xl p-8 border border-zinc-100 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 rounded-xl flex items-center justify-center mb-6">
                <Building2 size={24} />
              </div>
              <h4 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Organismes Acheteurs</h4>
              <ul className="space-y-3">
                {['Ministère de l\'Équipement', 'Autoroutes du Maroc (ADM)', 'Agence Nationale des Ports', 'Tanger Med (TMSA)'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300 font-medium">
                    <ShieldCheck size={16} className="text-emerald-500" /> {item}
                  </li>
                ))}
              </ul>
            </div>
 
            {/* Activités */}
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-2xl p-8 border border-zinc-100 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/40 text-orange-600 dark:text-orange-400 rounded-xl flex items-center justify-center mb-6">
                <Briefcase size={24} />
              </div>
              <h4 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Domaines d'Activité</h4>
              <ul className="space-y-3">
                {['Bâtiments et Génie Civil', 'Travaux de Terrassements', 'Plomberie & Climatisation', 'Études et Services'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300 font-medium">
                    <ShieldCheck size={16} className="text-emerald-500" /> {item}
                  </li>
                ))}
              </ul>
            </div>
 
            {/* Géographie */}
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-2xl p-8 border border-zinc-100 dark:border-zinc-700 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center mb-6">
                <MapPin size={24} />
              </div>
              <h4 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4">Régions Couvertes</h4>
              <ul className="space-y-3">
                {['Toutes les villes du Maroc', 'Souss Massa Draa', 'Région Grand Casablanca', 'Nador Westmed'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300 font-medium">
                    <ShieldCheck size={16} className="text-emerald-500" /> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>
 
      {/* Features Section — reste sombre volontairement, quel que soit le thème */}
      <section className="relative z-10 py-24 bg-zinc-900 text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold mb-4">Fonctionnalités Technologiques</h3>
            <p className="text-zinc-400 max-w-2xl mx-auto">Une architecture moderne pour maîtriser le cycle de vie de la donnée des marchés publics.</p>
          </div>
 
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { icon: ScanText, title: 'Extraction OCR Native', desc: 'Lecture automatisée des PDF scannés (Avis, CPS, RC) via Tesseract & Vision IA.', color: 'text-blue-400' },
              { icon: BrainCircuit, title: 'Anomalies ML', desc: 'Modèles de Machine Learning pour détecter les délais ou budgets suspects.', color: 'text-purple-400' },
              { icon: Search, title: 'Moteur Sémantique FTS', desc: 'Recherche plein texte ultra-rapide dans l\'intégralité des documents archivés.', color: 'text-emerald-400' },
              { icon: BarChart3, title: 'BI & KPIs', desc: 'Tableaux de bords dynamiques pour piloter les investissements par région et secteur.', color: 'text-orange-400' }
            ].map((feat, i) => (
              <div key={i} className="bg-zinc-800/50 border border-zinc-700/50 rounded-2xl p-6 hover:bg-zinc-800 transition-colors">
                <feat.icon size={32} className={`mb-4 ${feat.color}`} strokeWidth={1.5} />
                <h4 className="text-lg font-semibold mb-2">{feat.title}</h4>
                <p className="text-sm text-zinc-400 leading-relaxed">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Footer — reste sombre volontairement, quel que soit le thème */}
      <footer className="relative z-10 bg-zinc-950 py-8 text-center border-t border-zinc-900">
        <p className="text-zinc-500 text-sm">© {new Date().getFullYear()} Plateforme GED Intelligente - PFA. Développé avec React, FastAPI & Playwright.</p>
      </footer>
    </div>
  );
};
 
export default LandingPage;
 