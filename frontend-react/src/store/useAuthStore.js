import { create } from 'zustand';
import { persist } from 'zustand/middleware';
 
const useAuthStore = create(
  persist(
    (set) => ({
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
    }),
    {
      name: 'auth-storage', // clé utilisée dans le localStorage du navigateur
    }
  )
);
 
export default useAuthStore;
 