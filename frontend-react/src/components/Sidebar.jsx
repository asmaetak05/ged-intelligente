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
    <aside data-testid="sidebar" className="w-60 border-r border-zinc-200 bg-[#fafafa] flex flex-col">
      <div className="p-6">
        <h1 className="text-sm font-semibold tracking-wide text-zinc-900">SYSTEME GED</h1>
        <p className="text-xs text-zinc-500 mt-1">v2.0 • PFA</p>
      </div>
      <nav aria-label="Menu principal" className="flex-1 px-4 py-2 space-y-1 overflow-y-auto">
        {menu.map((item, idx) => {
          const isActive = currentPath === item.path;
          return (
            <Link data-testid={`sidebar-link-${item.path.replace('/', '')}`} key={idx} to={item.path} className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${isActive ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium' : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100/50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-zinc-100'}`}>
              <item.icon aria-hidden="true" size={16} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'text-zinc-900 dark:text-zinc-100' : 'text-zinc-500 dark:text-zinc-400'} />
              {item.name}
            </Link>
          )
        })}
        <div className="pt-4 mt-4 border-t border-zinc-200 dark:border-zinc-800">
          <p className="px-3 text-xs font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider mb-2">Administration</p>
          <Link to="/users" className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${currentPath === '/users' ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium' : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100/50 dark:hover:bg-zinc-800/50'}`}>
            <Server size={16} strokeWidth={2} /> Utilisateurs
          </Link>
          <Link to="/audit" className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${currentPath === '/audit' ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium' : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100/50 dark:hover:bg-zinc-800/50'}`}>
            <Activity size={16} strokeWidth={2} /> Traçabilité
          </Link>
        </div>
      </nav>
      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800">
        <Link to="/profile" data-testid="sidebar-user-profile" className="flex items-center gap-3 hover:bg-zinc-100 dark:hover:bg-zinc-800 p-2 rounded-md transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold text-xs">
            AD
          </div>
          <div className="text-xs">
            <p className="font-medium text-zinc-900 dark:text-zinc-100">Admin User</p>
            <p className="text-zinc-500 dark:text-zinc-400">Gérer le profil</p>
          </div>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;
