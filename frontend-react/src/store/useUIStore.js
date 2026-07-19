import { create } from 'zustand';

const useUIStore = create((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  
  isDarkMode: false,
  toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  
  kpisCache: null,
  setKpisCache: (data) => set({ kpisCache: data }),
  clearKpisCache: () => set({ kpisCache: null }),
}));

export default useUIStore;
