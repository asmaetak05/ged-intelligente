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
    <div className="flex flex-col">
      {/* Official Top Bar */}
      <div className="bg-primary-dark text-white px-6 py-2 text-xs flex justify-between items-center border-b-2 border-accent-gold">
        <div className="flex items-center gap-4">
          <span className="font-arabic text-sm">المملكة المغربية - وزارة التجهيز والماء</span>
          <span className="opacity-40">|</span>
          <span className="font-medium">Royaume du Maroc - Ministère de l'Équipement et de l'Eau</span>
        </div>
        <div className="flex gap-4 items-center">
          <span className="font-bold text-accent-lime">FR / AR</span>
        </div>
      </div>

      {/* Main Topbar */}
      <header data-testid="topbar" className="h-16 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center bg-primary-dark text-accent-gold">
            {/* SVG Logo Placeholder */}
            <svg width="24" height="24" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" stroke="#C5A059" strokeWidth="6" fill="#0F2C3A"/>
                <path d="M50 15 L58 38 L82 38 L63 52 L70 75 L50 60 L30 75 L37 52 L18 38 L42 38 Z" fill="#85E05D"/>
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-bold text-primary-dark dark:text-white leading-tight">GED INTELLIGENTE</h1>
            <p className="text-[10px] font-semibold text-primary-accent uppercase">Portail National</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-text-muted">
          <button 
            aria-label={isDarkMode ? "Passer en mode clair" : "Passer en mode sombre"}
            onClick={toggleDarkMode}
            className="hover:text-primary-accent transition-colors"
          >
            {isDarkMode ? <Sun aria-hidden="true" size={18} /> : <Moon aria-hidden="true" size={18} />}
          </button>
          <button aria-label="Notifications" data-testid="topbar-notifications-btn" className="hover:text-primary-accent transition-colors">
            <Bell aria-hidden="true" size={18} />
          </button>
          <button aria-label="Se déconnecter" onClick={handleLogout} className="hover:text-red-500 transition-colors ml-2">
            <LogOut aria-hidden="true" size={18} />
          </button>
        </div>
      </header>
    </div>
  );
};

export default Topbar;
