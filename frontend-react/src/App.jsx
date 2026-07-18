import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './components/Dashboard';
import SearchFTS from './components/SearchFTS';
import Explorer from './components/Explorer';
import DocumentDetail from './components/DocumentDetail';
import Upload from './components/Upload';
import PredictorML from './components/PredictorML';
import Monitoring from './components/Monitoring';
import Placeholder from './components/Placeholder';
import PipelineAdmin from './components/PipelineAdmin';
import LandingPage from './components/LandingPage';

const LayoutWrapper = ({ children }) => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  if (isLandingPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#fafafa] text-[#111111] font-sans selection:bg-zinc-200">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/search" element={<SearchFTS />} />
                <Route path="/document/:numero" element={<DocumentDetail />} />
                <Route path="/explorer" element={<Explorer />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/ml" element={<PredictorML />} />
                <Route path="/monitoring" element={<Monitoring />} />
                <Route path="/pipeline" element={<PipelineAdmin />} />
                <Route path="*" element={<Placeholder title="Page Introuvable" />} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
