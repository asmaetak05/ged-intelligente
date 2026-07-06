import React from 'react';
import { Bell } from 'lucide-react';

const Topbar = () => {
  return (
    <header className="h-16 border-b border-zinc-200 bg-[#fafafa] flex items-center justify-between px-8">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
        <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Services opérationnels</span>
      </div>
      <div className="flex items-center gap-4 text-zinc-400">
        <button className="hover:text-zinc-600 transition-colors">
          <Bell size={18} />
        </button>
      </div>
    </header>
  );
};

export default Topbar;
