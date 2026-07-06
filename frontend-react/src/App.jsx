import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './components/Dashboard';
import SearchFTS from './components/SearchFTS';
import Explorer from './components/Explorer';
import Upload from './components/Upload';
import PredictorML from './components/PredictorML';
import Monitoring from './components/Monitoring';
import Placeholder from './components/Placeholder';

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-[#fafafa] text-[#111111] font-sans selection:bg-zinc-200">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto">
            <div className="max-w-6xl mx-auto w-full">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/search" element={<SearchFTS />} />
                <Route path="/explorer" element={<Explorer />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/ml" element={<PredictorML />} />
                <Route path="/monitoring" element={<Monitoring />} />
                <Route path="*" element={<Placeholder title="Page Introuvable" />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
