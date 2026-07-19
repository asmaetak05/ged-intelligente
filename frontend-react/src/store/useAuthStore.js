import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: (userData, userToken) => set({ 
    user: userData, 
    token: userToken, 
    isAuthenticated: true 
  }),
  
  logout: () => set({ 
    user: null, 
    token: null, 
    isAuthenticated: false 
  }),
}));

export default useAuthStore;
