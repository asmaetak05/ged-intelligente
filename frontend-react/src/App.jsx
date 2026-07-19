import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from 'sonner';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import ProtectedRoute from './components/ProtectedRoute';
import useUIStore from './store/useUIStore';
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts';

const Dashboard = lazy(() => import('./components/Dashboard'));
const SearchFTS = lazy(() => import('./components/SearchFTS'));
const Explorer = lazy(() => import('./components/Explorer'));
const DocumentDetail = lazy(() => import('./components/DocumentDetail'));
const Upload = lazy(() => import('./components/Upload'));
const PredictorML = lazy(() => import('./components/PredictorML'));
const Monitoring = lazy(() => import('./components/Monitoring'));
const PipelineAdmin = lazy(() => import('./components/PipelineAdmin'));
const LandingPage = lazy(() => import('./components/LandingPage'));

const Login = lazy(() => import('./pages/Login'));
const Profile = lazy(() => import('./pages/Profile'));
const Users = lazy(() => import('./pages/Users'));
const Audit = lazy(() => import('./pages/Audit'));
const NotFound = lazy(() => import('./pages/errors/NotFound'));
const Forbidden = lazy(() => import('./pages/errors/Forbidden'));
const ServerError = lazy(() => import('./pages/errors/ServerError'));

const LoadingFallback = () => (
  <div className="flex h-screen w-full items-center justify-center bg-[#fafafa] dark:bg-zinc-900">
    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

const LayoutWrapper = ({ children }) => {
  const location = useLocation();
  const isPublicPage = ['/', '/login', '/404', '/403', '/500'].includes(location.pathname);
  useKeyboardShortcuts();

  if (isPublicPage) {
    return <Suspense fallback={<LoadingFallback />}>{children}</Suspense>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#fafafa] dark:bg-zinc-900 text-[#111111] dark:text-zinc-100 font-sans selection:bg-zinc-200 dark:selection:bg-zinc-700">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            <Suspense fallback={<LoadingFallback />}>
              {children}
            </Suspense>
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  const isDarkMode = useUIStore((state) => state.isDarkMode);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <Router>
      <Toaster richColors position="bottom-right" />
      <LayoutWrapper>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/404" element={<NotFound />} />
          <Route path="/403" element={<Forbidden />} />
          <Route path="/500" element={<ServerError />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/search" element={<SearchFTS />} />
            <Route path="/document/:numero" element={<DocumentDetail />} />
            <Route path="/explorer" element={<Explorer />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/ml" element={<PredictorML />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/pipeline" element={<PipelineAdmin />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/audit" element={<Audit />} />
          </Route>

          <Route element={<ProtectedRoute requireAdmin={true} />}>
            <Route path="/users" element={<Users />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
