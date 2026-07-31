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

  const COLORS = ['#0F2C3A', '#00A86B', '#85E05D', '#C5A059', '#1A3C40'];

  return (
    <div className="p-8 relative min-h-full">
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: `url(${texture})`, backgroundSize: 'cover', backgroundPosition: 'center', opacity: 0.05 }}></div>
      <div className="relative z-10">
        <div className="mb-8 border-l-4 border-primary-accent pl-4">
          <h2 className="text-2xl font-bold text-primary-dark">Vue d'ensemble</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {loadingKpis ? (
            Array(4).fill(0).map((_, i) => (
              <div key={i} className="bg-white p-6 border border-border-color rounded-md shadow-sm">
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
              <div key={i} className="bg-white p-6 border border-border-color rounded-md shadow-sm hover:shadow-md transition-shadow flex flex-col justify-center">
                <p className="text-xs text-text-muted font-bold uppercase tracking-wide mb-1">{kpi.label}</p>
                <p className="text-3xl font-extrabold text-primary-dark">{kpi.value}</p>
              </div>
            ))
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 border border-border-color rounded-md shadow-sm flex flex-col h-[400px]">
            <h3 className="text-base font-bold text-primary-dark mb-6">Répartition Sectorielle</h3>
            {loadingCharts ? (
               <Skeleton className="w-full flex-1" />
            ) : (
              <>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={categories} innerRadius={75} outerRadius={95} paddingAngle={3} dataKey="value" stroke="none">
                        {categories.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center flex-wrap gap-4 mt-4 text-xs font-medium text-text-muted shrink-0">
                  {categories.map((c, i) => (
                    <div key={i} className="flex items-center gap-2"><span className="w-3 h-3 rounded-sm" style={{backgroundColor: COLORS[i%COLORS.length]}}></span>{c.name}</div>
                  ))}
                </div>
              </>
            )}
          </div>
          
          <div className="bg-white p-6 border border-border-color rounded-md shadow-sm flex flex-col h-[400px]">
            <h3 className="text-base font-bold text-primary-dark mb-6">Acheteurs Principaux</h3>
            {loadingCharts ? (
              <Skeleton className="w-full flex-1" />
            ) : (
              <div className="flex-1 min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={buyers} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="organisme" type="category" width={100} tick={{fontSize: 11, fill: '#64748B', fontWeight: 500}} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{fill: '#F4F7F6'}} contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }} />
                    <Bar dataKey="budget" fill="#00A86B" radius={[0, 4, 4, 0]} barSize={20} />
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
