'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { ShieldCheckIcon, ShieldExclamationIcon } from '@heroicons/react/24/solid';

// Dynamically import ApexCharts to prevent SSR issues
const ReactApexChart = dynamic(() => import('react-apexcharts'), { ssr: false });

interface SSHLog {
  timestamp?: string;
  username?: string;
  ip_address?: string;
  command?: string;
  session_id?: string;
  threat_level?: 'low' | 'medium' | 'high';
  threat_details?: {
    score: number;
    attack_types: string[];
    risk_indicators: string[];
  };
}

interface SSHLogsProps {
  logs?: SSHLog[];
}

const getThreatLevelColor = (level?: 'low' | 'medium' | 'high') => {
  switch (level) {
    case 'low':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-blue-100 text-blue-800';
  }
};

const SSHLogs = ({ logs = [] }: SSHLogsProps) => {
  const [threatData, setThreatData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreatData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/threats');
        if (!response.ok) {
          throw new Error('Failed to fetch threat data');
        }
        const data = await response.json();
        setThreatData(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
      }
    };

    fetchThreatData();
  }, []);

  // Safely handle logs and threat data
  const safeLogs = Array.isArray(logs) ? logs : [];
  const sortedLogs = [...safeLogs].sort(
    (a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime()
  );

  // Prepare chart data with safe checks
  const threatCounts = {
    low: threatData?.recent_threats?.filter((t: any) => t?.score <= 3).length || 0,
    medium: threatData?.recent_threats?.filter((t: any) => t?.score > 3 && t?.score <= 6).length || 0,
    high: threatData?.recent_threats?.filter((t: any) => t?.score > 6).length || 0,
  };

  const chartOptions = {
    chart: {
      type: 'donut',
    },
    labels: ['Risque Faible', 'Risque Moyen', 'Risque Élevé'],
    colors: ['#34d399', '#fbbf24', '#f87171'],
    legend: {
      position: 'bottom',
    },
  };

  const chartSeries = [threatCounts.low, threatCounts.medium, threatCounts.high];

  return (
    <div className="glass-card">
      {threatData && (
        <div className="mt-6 bg-blue-50/50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            Résumé des Menaces
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <p className="text-sm text-blue-800">Total des Menaces</p>
              <p className="text-2xl font-bold text-blue-900">
                {threatData.recent_threats?.length || 0}
              </p>
            </div>
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <p className="text-sm text-green-800">Risque Faible</p>
              <p className="text-2xl font-bold text-green-900">
                {threatData.recent_threats?.filter((t: any) => t.score <= 3).length || 0}
              </p>
            </div>
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <p className="text-sm text-yellow-800">Risque Moyen</p>
              <p className="text-2xl font-bold text-yellow-900">
                {threatData.recent_threats?.filter((t: any) => t.score > 3 && t.score <= 6).length || 0}
              </p>
            </div>
            <div className="bg-white p-3 rounded-lg shadow-sm">
              <p className="text-sm text-red-800">Risque Élevé</p>
              <p className="text-2xl font-bold text-red-900">
                {threatData.recent_threats?.filter((t: any) => t.score > 6).length || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Logs Table */}
      {logs && logs.length > 0 && (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-blue-200/10">
                <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                  Temps
                </th>
                <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                  Nom d'Utilisateur
                </th>
                <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                  Adresse IP
                </th>
                <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                  Action
                </th>
                <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                  Niveau de Menace
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-blue-200/10">
              {sortedLogs.map((log, index) => {
                const logThreatInfo = threatData?.recent_threats?.find(
                  (threat: any) => threat.ip === log.ip_address
                );

                return (
                  <tr key={index} className="hover:bg-blue-100/10 transition-colors">
                    <td className="py-3 px-4 text-sm text-blue-100">
                      {new Date(log.timestamp || '').toLocaleString('fr-FR')}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-blue-100">
                        {log.username || 'Inconnu'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-blue-100">
                      {log.ip_address || 'Inconnu'}
                    </td>
                    <td className="py-3 px-4">
                      {log.command ? (
                        <div className="glass px-3 py-1 rounded-lg text-xs text-blue-100 max-w-xs truncate">
                          {log.command}
                        </div>
                      ) : (
                        <span className="text-blue-200 text-xs">Aucune action</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {logThreatInfo ? (
                        <div 
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            getThreatLevelColor(
                              logThreatInfo.score > 6 ? 'high' : 
                              logThreatInfo.score > 3 ? 'medium' : 'low'
                            )
                          }`}
                        >
                          {logThreatInfo.score > 6 ? (
                            <ShieldExclamationIcon className="h-4 w-4 mr-1 text-red-600" />
                          ) : (
                            <ShieldCheckIcon className="h-4 w-4 mr-1 text-green-600" />
                          )}
                          {logThreatInfo.score > 6 ? 'Risque Élevé' : 
                           logThreatInfo.score > 3 ? 'Risque Moyen' : 'Risque Faible'}
                        </div>
                      ) : (
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-500/20 text-blue-200">
                          Non Évalué
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Chart Section */}
      {threatData && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Résumé des Menaces</h3>
          <ReactApexChart 
            options={{
              chart: {
                type: 'donut'
              },
              labels: ['Risque Faible', 'Risque Moyen', 'Risque Élevé'],
              series: [
                threatData.recent_threats.filter((t: any) => t.score <= 3).length,
                threatData.recent_threats.filter((t: any) => t.score > 3 && t.score <= 6).length,
                threatData.recent_threats.filter((t: any) => t.score > 6).length
              ]
            }}
            type="donut" 
            height={350} 
          />
        </div>
      )}
    </div>
  );
};

export default SSHLogs;
