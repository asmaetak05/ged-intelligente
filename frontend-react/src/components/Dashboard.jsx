import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [kpis, setKpis] = useState({ total_appels_offres: 0, volume_financier_total_mad: 0, delai_moyen_execution_mois: 0, taux_reussite_ocr_pct: 0 });
  const [categories, setCategories] = useState([]);
  const [buyers, setBuyers] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/v1/analytics/kpis').then(res => setKpis(res.data)).catch(() => console.error("API error"));
    axios.get('http://127.0.0.1:8000/api/v1/analytics/distribution/categories').then(res => {
      const mapped = res.data.map(item => ({ name: item.categorie, value: item.count }));
      setCategories(mapped);
    }).catch(() => console.error("API error"));
    axios.get('http://127.0.0.1:8000/api/v1/analytics/top-buyers').then(res => setBuyers(res.data)).catch(() => console.error("API error"));
  }, []);

  const COLORS = ['#18181b', '#52525b', '#a1a1aa', '#e4e4e7'];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-xl font-medium text-zinc-900">Vue d'ensemble</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Projets", value: kpis.total_appels_offres },
          { label: "Volume (MAD)", value: `${(kpis.volume_financier_total_mad/1000000).toFixed(1)}M` },
          { label: "Délai Moyen", value: `${kpis.delai_moyen_execution_mois}m` },
          { label: "Fiabilité OCR", value: `${kpis.taux_reussite_ocr_pct}%` },
        ].map((kpi, i) => (
          <div key={i} className="bg-white p-5 border border-zinc-200 rounded-md">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">{kpi.label}</p>
            <p className="text-2xl font-light text-zinc-900">{kpi.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white p-6 border border-zinc-200 rounded-md">
          <h3 className="text-sm font-medium text-zinc-800 mb-6">Répartition Sectorielle</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categories} innerRadius={70} outerRadius={80} paddingAngle={2} dataKey="value" stroke="none">
                  {categories.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '4px', border: '1px solid #e4e4e7', boxShadow: 'none' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2 text-xs text-zinc-500">
            {categories.map((c, i) => (
              <div key={i} className="flex items-center gap-2"><span className="w-2 h-2 rounded-sm" style={{backgroundColor: COLORS[i%COLORS.length]}}></span>{c.name}</div>
            ))}
          </div>
        </div>
        
        <div className="bg-white p-6 border border-zinc-200 rounded-md">
          <h3 className="text-sm font-medium text-zinc-800 mb-6">Acheteurs Principaux</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={buyers} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="organisme" type="category" width={100} tick={{fontSize: 11, fill: '#71717a'}} axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: '#f4f4f5'}} contentStyle={{ borderRadius: '4px', border: '1px solid #e4e4e7', boxShadow: 'none' }} />
                <Bar dataKey="budget" fill="#27272a" radius={[0, 2, 2, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
