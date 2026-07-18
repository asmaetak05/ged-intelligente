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
    <aside className="w-60 border-r border-zinc-200 bg-[#fafafa] flex flex-col">
      <div className="p-6">
        <h1 className="text-sm font-semibold tracking-wide text-zinc-900">SYSTEME GED</h1>
        <p className="text-xs text-zinc-500 mt-1">v2.0 • PFA</p>
      </div>
      <nav className="flex-1 px-4 py-2 space-y-1">
        {menu.map((item, idx) => {
          const isActive = currentPath === item.path;
          return (
            <Link key={idx} to={item.path} className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${isActive ? 'bg-zinc-100 text-zinc-900 font-medium' : 'text-zinc-600 hover:bg-zinc-100/50 hover:text-zinc-900'}`}>
              <item.icon size={16} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'text-zinc-900' : 'text-zinc-500'} />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="p-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-zinc-200 border border-zinc-300"></div>
          <div className="text-xs">
            <p className="font-medium text-zinc-900">Admin</p>
            <p className="text-zinc-500">Service Marchés</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
