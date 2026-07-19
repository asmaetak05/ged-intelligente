import React from 'react';
import { Bell, Moon, Sun, LogOut } from 'lucide-react';
import useUIStore from '../store/useUIStore';
import useAuthStore from '../store/useAuthStore';
import { useNavigate } from 'react-router-dom';

const Topbar = () => {
  const isDarkMode = useUIStore((state) => state.isDarkMode);
  const toggleDarkMode = useUIStore((state) => state.toggleDarkMode);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header data-testid="topbar" className="h-16 border-b border-zinc-200 dark:border-zinc-800 bg-[#fafafa] dark:bg-zinc-900 flex items-center justify-between px-8">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
        <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Services opérationnels</span>
      </div>
      <div className="flex items-center gap-4 text-zinc-400">
        <button 
          aria-label={isDarkMode ? "Passer en mode clair" : "Passer en mode sombre"}
          onClick={toggleDarkMode}
          className="hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
        >
          {isDarkMode ? <Sun aria-hidden="true" size={18} /> : <Moon aria-hidden="true" size={18} />}
        </button>
        <button aria-label="Notifications" data-testid="topbar-notifications-btn" className="hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors">
          <Bell aria-hidden="true" size={18} />
        </button>
        <button aria-label="Se déconnecter" onClick={handleLogout} className="hover:text-red-500 transition-colors ml-2">
          <LogOut aria-hidden="true" size={18} />
        </button>
      </div>
    </header>
  );
};

export default Topbar;
