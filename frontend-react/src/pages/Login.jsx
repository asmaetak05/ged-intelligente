import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';
import useAuthStore from '../store/useAuthStore';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().min(1, 'L\'email est requis').email('Format d\'email invalide'),
  password: z.string().min(6, 'Le mot de passe doit contenir au moins 6 caractères'),
});

const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);

    try {
      // Simulation appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const mockUser = {
        id: 1,
        email: data.email,
        name: data.email.split('@')[0],
        role: data.email.includes('admin') ? 'admin' : 'user'
      };
      const mockToken = 'mock-jwt-token-12345';
      
      login(mockUser, mockToken);
      toast.success(`Bienvenue, ${mockUser.name}`);
      navigate('/dashboard');
    } catch (err) {
      toast.error('Erreur lors de la connexion');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900 transition-colors">
      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-zinc-800 rounded-xl shadow-sm border border-gray-100 dark:border-zinc-700">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-zinc-100">GED Intelligente</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-zinc-400">Connectez-vous à votre compte</p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-zinc-300">Email</label>
              <div className="relative mt-1">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <Mail className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  {...register('email')}
                  className={`block w-full py-2 pl-10 pr-3 border ${errors.email ? 'border-red-500' : 'border-gray-300 dark:border-zinc-600'} rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-zinc-900 text-gray-900 dark:text-zinc-100 sm:text-sm`}
                  placeholder="admin@example.com"
                />
              </div>
              {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-zinc-300">Mot de passe</label>
              <div className="relative mt-1">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  type="password"
                  {...register('password')}
                  className={`block w-full py-2 pl-10 pr-3 border ${errors.password ? 'border-red-500' : 'border-gray-300 dark:border-zinc-600'} rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-zinc-900 text-gray-900 dark:text-zinc-100 sm:text-sm`}
                  placeholder="••••••••"
                />
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
