import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Search, Folder, UploadCloud, BrainCircuit, Activity, Server } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  const menu = [
    { name: 'Vue d\'ensemble', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'Recherche FTS', icon: Search, path: '/search' },
    { name: 'Explorateur', icon: Folder, path: '/explorer' },
    { name: 'Ingestion', icon: UploadCloud, path: '/upload' },
    { name: 'Modèles ML', icon: BrainCircuit, path: '/ml' },
    { name: 'Monitoring', icon: Activity, path: '/monitoring' },
    { name: 'Pipeline & Admin', icon: Server, path: '/pipeline' },
  ];

  return (
    <aside data-testid="sidebar" className="w-64 bg-primary-dark text-white flex flex-col h-full overflow-hidden shadow-lg border-r border-secondary-dark">
      <div className="p-6 border-b border-white/10">
        <h1 className="text-sm font-bold tracking-wide text-white flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-accent-gold flex items-center justify-center text-primary-dark">
            <Folder size={14} />
          </div>
          SYSTEME GED
        </h1>
        <p className="text-xs text-zinc-400 mt-2 font-medium">Portail Ministériel v2.0</p>
      </div>
      <nav aria-label="Menu principal" className="flex-1 px-4 py-4 space-y-1.5 overflow-y-auto">
        {menu.map((item, idx) => {
          const isActive = currentPath === item.path;
          return (
            <Link data-testid={`sidebar-link-${item.path.replace('/', '')}`} key={idx} to={item.path} className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${isActive ? 'bg-primary-accent/20 text-accent-lime' : 'text-zinc-300 hover:bg-white/10 hover:text-white'}`}>
              <item.icon aria-hidden="true" size={18} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'text-accent-lime' : 'text-zinc-400'} />
              {item.name}
            </Link>
          )
        })}
        <div className="pt-6 mt-4 border-t border-white/10">
          <p className="px-3 text-xs font-bold text-zinc-500 uppercase tracking-wider mb-3">Administration</p>
          <Link to="/users" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentPath === '/users' ? 'bg-primary-accent/20 text-accent-lime' : 'text-zinc-300 hover:bg-white/10 hover:text-white'}`}>
            <Server size={18} strokeWidth={2} /> Utilisateurs
          </Link>
          <Link to="/audit" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${currentPath === '/audit' ? 'bg-primary-accent/20 text-accent-lime' : 'text-zinc-300 hover:bg-white/10 hover:text-white'}`}>
            <Activity size={18} strokeWidth={2} /> Traçabilité
          </Link>
        </div>
      </nav>
      <div className="p-4 border-t border-white/10 bg-secondary-dark/50">
        <Link to="/profile" data-testid="sidebar-user-profile" className="flex items-center gap-3 hover:bg-white/10 p-2.5 rounded-lg transition-colors cursor-pointer">
          <div className="w-9 h-9 rounded-full bg-primary-accent text-white flex items-center justify-center font-bold text-sm shadow-sm">
            AD
          </div>
          <div className="text-sm">
            <p className="font-semibold text-white">Admin User</p>
            <p className="text-xs text-zinc-400">Gérer le profil</p>
          </div>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;
