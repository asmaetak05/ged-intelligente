import React, { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import texture from '../assets/texture.jpg';
import Skeleton from './Skeleton';
 
const Dashboard = () => {
  const [kpis, setKpis] = useState({ total_appels_offres: 0, volume_financier_total_mad: 0, delai_moyen_execution_mois: 0, taux_reussite_ocr_pct: 0 });
  const [categories, setCategories] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [loadingKpis, setLoadingKpis] = useState(true);
  const [loadingCharts, setLoadingCharts] = useState(true);
 
  useEffect(() => {
    // Fetch KPIs
    apiClient.get('/api/v1/analytics/kpis')
      .then(res => {
        setKpis(res.data);
      })
      .catch(() => console.error("API error KPIs"))
      .finally(() => setLoadingKpis(false));
 
    // Fetch Charts data
    Promise.all([
      apiClient.get('/api/v1/analytics/distribution/categories'),
      apiClient.get('/api/v1/analytics/top-buyers')
    ])
    .then(([catRes, buyersRes]) => {
      const mapped = catRes.data.map(item => ({ name: item.categorie, value: item.count }));
      setCategories(mapped);
      setBuyers(buyersRes.data);
    })
    .catch(() => console.error("API error Charts"))
    .finally(() => setLoadingCharts(false));
  }, []);
 
  const COLORS = ['#18181b', '#52525b', '#a1a1aa', '#e4e4e7'];
 
  return (
    <div className="p-8 relative min-h-full">
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: `url(${texture})`, backgroundSize: 'cover', backgroundPosition: 'center', opacity: 0.07 }}></div>
      <div className="relative z-10">
        <div className="mb-8">
          <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100">Vue d'ensemble</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {loadingKpis ? (
            Array(4).fill(0).map((_, i) => (
              <div key={i} className="bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm p-5 border border-zinc-200 dark:border-zinc-700 rounded-md">
                <Skeleton className="h-3 w-20 mb-3" />
                <Skeleton className="h-8 w-16" />
              </div>
            ))
          ) : (
            [
              { label: "Total Projets", value: kpis.total_appels_offres },
              { label: "Volume (MAD)", value: `${(kpis.volume_financier_total_mad/1000000).toFixed(1)}M` },
              { label: "Délai Moyen", value: `${kpis.delai_moyen_execution_mois}m` },
              { label: "Fiabilité OCR", value: `${kpis.taux_reussite_ocr_pct}%` },
            ].map((kpi, i) => (
              <div key={i} className="bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm p-5 border border-zinc-200 dark:border-zinc-700 rounded-md">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">{kpi.label}</p>
                <p className="text-2xl font-light text-zinc-900 dark:text-zinc-100">{kpi.value}</p>
              </div>
            ))
          )}
        </div>
 
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm p-6 border border-zinc-200 dark:border-zinc-700 rounded-md flex flex-col h-[380px]">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-6">Répartition Sectorielle</h3>
            {loadingCharts ? (
               <Skeleton className="w-full flex-1" />
            ) : (
              <>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={categories} innerRadius={70} outerRadius={80} paddingAngle={2} dataKey="value" stroke="none">
                        {categories.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: '4px', border: '1px solid #e4e4e7', boxShadow: 'none' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center flex-wrap gap-4 mt-4 text-xs text-zinc-500 dark:text-zinc-400 shrink-0">
                  {categories.map((c, i) => (
                    <div key={i} className="flex items-center gap-2"><span className="w-2 h-2 rounded-sm" style={{backgroundColor: COLORS[i%COLORS.length]}}></span>{c.name}</div>
                  ))}
                </div>
              </>
            )}
          </div>
          
          <div className="bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm p-6 border border-zinc-200 dark:border-zinc-700 rounded-md flex flex-col h-[380px]">
            <h3 className="text-sm font-medium text-zinc-800 dark:text-zinc-200 mb-6">Acheteurs Principaux</h3>
            {loadingCharts ? (
              <Skeleton className="w-full flex-1" />
            ) : (
              <div className="flex-1 min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={buyers} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="organisme" type="category" width={100} tick={{fontSize: 11, fill: '#71717a'}} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{fill: '#f4f4f5'}} contentStyle={{ borderRadius: '4px', border: '1px solid #e4e4e7', boxShadow: 'none' }} />
                    <Bar dataKey="budget" fill="#27272a" radius={[0, 2, 2, 0]} barSize={16} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
 
export default Dashboard;