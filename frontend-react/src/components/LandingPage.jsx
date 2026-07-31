import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BarChart3, BrainCircuit, Search, ScanText, ShieldCheck, MapPin, Building2, Briefcase } from 'lucide-react';
import logo from '../assets/logo.jpg';
import texture from '../assets/texture.jpg';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg-light font-main selection:bg-primary-accent selection:text-white relative">
      {/* Texture Background */}
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: `url(${texture})`, backgroundSize: 'cover', backgroundPosition: 'center', opacity: 0.05 }}></div>
      
      {/* Top Official Bar */}
      <div className="bg-primary-dark text-white px-6 py-2 text-xs flex justify-between items-center border-b-2 border-accent-gold relative z-10">
        <div className="flex items-center gap-4 max-w-7xl mx-auto w-full">
          <span className="font-arabic text-sm">المملكة المغربية - وزارة التجهيز والماء</span>
          <span className="opacity-40">|</span>
          <span className="font-medium">Royaume du Maroc - Ministère de l'Équipement et de l'Eau</span>
        </div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-white shadow-sm sticky top-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src={logo} alt="Royaume du Maroc - Ministère de l'Equipement" className="h-12 object-contain" />
            <div className="h-8 w-px bg-zinc-300 mx-2"></div>
            <div>
              <h1 className="text-lg font-bold text-primary-dark leading-tight">GED Intelligente</h1>
              <p className="text-xs font-semibold text-primary-accent tracking-wider uppercase">Plateforme Décisionnelle</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/pipeline')}
              className="text-sm font-medium text-text-muted hover:text-primary-dark transition-colors"
            >
              Pipeline Admin
            </button>
            <button 
              onClick={() => navigate('/dashboard')}
              className="bg-primary-accent hover:bg-emerald-700 text-white px-6 py-2.5 rounded-pill text-sm font-bold transition-all shadow-md flex items-center gap-2"
            >
              Accéder au Dashboard <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-to-br from-primary-dark to-[#081B26] rounded-lg overflow-hidden text-white relative p-10 shadow-lg border-t-4 border-accent-gold">
            <div className="grid md:grid-cols-2 gap-10 items-center">
              <div>
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-pill bg-accent-lime/10 border border-accent-lime/30 text-accent-lime text-xs font-bold mb-6 tracking-wide uppercase">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-lime opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-lime"></span>
                  </span>
                  Système de Gestion des Marchés Publics V2.0
                </div>
                <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-[1.2] mb-6">
                  La donnée des appels d'offres, <br/>
                  <span className="text-accent-lime">décryptée par l'IA.</span>
                </h2>
                <p className="text-zinc-300 mb-8 max-w-lg leading-relaxed">
                  Centralisez, analysez et précevez les tendances des marchés publics. 
                  Grâce à la combinaison de l'OCR et du Machine Learning, transformez les archives brutes en tableaux de bord stratégiques.
                </p>
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="bg-accent-lime text-primary-dark px-8 py-3.5 rounded-pill text-base font-bold transition-all shadow-lg flex items-center gap-2 hover:bg-[#73d04b]"
                >
                  Explorer la base de données <Search size={18} />
                </button>
              </div>
              <div className="relative">
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-md p-6 shadow-2xl">
                   <img 
                    src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80" 
                    alt="Dashboard BI Preview" 
                    className="w-full h-48 object-cover rounded shadow-md opacity-80 mix-blend-luminosity"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Cards Grid */}
      <section className="relative z-10 py-16 bg-bg-light border-y border-border-color">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-primary-dark mb-4 border-l-4 border-primary-accent pl-4 inline-block">Couverture & Expertise</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-md p-8 shadow-md border-t-4 border-transparent hover:-translate-y-1 transition-all">
              <div className="w-14 h-14 bg-primary-accent/10 text-primary-accent rounded-sm flex items-center justify-center mb-6">
                <Building2 size={28} />
              </div>
              <h4 className="text-lg font-bold text-primary-dark mb-4">Organismes Acheteurs</h4>
              <ul className="space-y-3">
                {["Ministère de l'Équipement", "Autoroutes du Maroc (ADM)", "Agence Nationale des Ports", "Tanger Med (TMSA)"].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-text-muted font-medium">
                    <ShieldCheck size={16} className="text-primary-accent" /> {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-primary-dark rounded-md p-8 shadow-md hover:-translate-y-1 transition-all text-white">
              <div className="w-14 h-14 bg-white/10 text-accent-lime rounded-sm flex items-center justify-center mb-6">
                <Briefcase size={28} />
              </div>
              <h4 className="text-lg font-bold mb-4">Domaines d'Activité</h4>
              <ul className="space-y-3">
                {['Bâtiments et Génie Civil', 'Travaux de Terrassements', 'Plomberie & Climatisation', 'Études et Services'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-zinc-300 font-medium">
                    <ShieldCheck size={16} className="text-accent-lime" /> {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-accent-lime rounded-md p-8 shadow-md hover:-translate-y-1 transition-all text-primary-dark">
              <div className="w-14 h-14 bg-primary-dark text-accent-lime rounded-sm flex items-center justify-center mb-6">
                <MapPin size={28} />
              </div>
              <h4 className="text-lg font-bold mb-4">Régions Couvertes</h4>
              <ul className="space-y-3">
                {['Toutes les villes du Maroc', 'Souss Massa Draa', 'Région Grand Casablanca', 'Nador Westmed'].map((item, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-[#2C4A1E] font-bold">
                    <ShieldCheck size={16} className="text-primary-dark" /> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Section */}
      <section className="relative z-10 py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-primary-dark mb-4 border-l-4 border-accent-gold pl-4 inline-block">Fonctionnalités Technologiques</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: ScanText, title: 'Extraction OCR Native', desc: 'Lecture automatisée des PDF scannés via Tesseract & Vision IA.', color: 'text-primary-accent', bg: 'bg-primary-accent/10' },
              { icon: BrainCircuit, title: 'Anomalies ML', desc: 'Modèles de Machine Learning pour détecter les retards ou dérives.', color: 'text-accent-gold', bg: 'bg-accent-gold/10' },
              { icon: Search, title: 'Moteur FTS', desc: 'Recherche sémantique ultra-rapide dans les documents.', color: 'text-primary-dark', bg: 'bg-primary-dark/10' },
              { icon: BarChart3, title: 'BI & KPIs', desc: 'Tableaux de bords dynamiques pour le pilotage.', color: 'text-accent-lime', bg: 'bg-accent-lime/20' }
            ].map((feat, i) => (
              <div key={i} className="border border-border-color rounded-md p-6 hover:shadow-md transition-shadow bg-white">
                <div className={`w-12 h-12 rounded-sm flex items-center justify-center mb-4 ${feat.bg} ${feat.color}`}>
                  <feat.icon size={24} strokeWidth={2} />
                </div>
                <h4 className="text-base font-bold text-primary-dark mb-2">{feat.title}</h4>
                <p className="text-sm text-text-muted leading-relaxed">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="relative z-10 bg-secondary-dark py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-zinc-400">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-full bg-primary-dark border border-white/10 flex items-center justify-center text-accent-gold">
               <Building2 size={14} />
             </div>
             <div>
               <p className="font-bold text-white uppercase">Ministère de l'Équipement et de l'Eau</p>
               <p>Royaume du Maroc</p>
             </div>
          </div>
          <p>© {new Date().getFullYear()} Plateforme GED Intelligente. Tous droits réservés.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
