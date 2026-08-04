import axios from 'axios';
import { toast } from 'sonner';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

import useAuthStore from '../store/useAuthStore';

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const status = error.response.status;
      const message = error.response.data?.detail || error.response.data?.message || 'Une erreur est survenue';
      
      toast.error(`Erreur ${status}: ${message}`);
    } else if (error.request) {
      // The request was made but no response was received
      toast.error('Erreur réseau : Impossible de contacter le serveur.');
    } else {
      // Something happened in setting up the request that triggered an Error
      toast.error(`Erreur : ${error.message}`);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
