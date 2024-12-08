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
        const response = await fetch('http://57.129.78.111:5000/api/threats');
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
    const interval = setInterval(fetchThreatData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Safely handle logs and threat data
  const safeLogs = Array.isArray(logs) ? logs : [];
  const sortedLogs = [...safeLogs].sort(
    (a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime()
  );

  const chartOptions = {
    chart: {
      type: 'donut',
      background: 'transparent',
      foreColor: '#1e40af'
    },
    labels: ['Risque Faible', 'Risque Moyen', 'Risque Élevé'],
    colors: ['#10B981', '#F59E0B', '#EF4444'],
    legend: {
      position: 'bottom',
      horizontalAlign: 'center',
      labels: {
        colors: '#1e40af'
      }
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: true,
            total: {
              show: true,
              label: 'Total des Menaces',
              color: '#1e40af'
            }
          }
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function(val: number, opts: any) {
        return opts.w.config.series[opts.seriesIndex];
      }
    },
    tooltip: {
      theme: 'dark'
    },
    responsive: [{
      breakpoint: 480,
      options: {
        chart: {
          width: 280
        },
        legend: {
          position: 'bottom'
        }
      }
    }]
  };

  return (
    <div className="glass-card p-6 rounded-lg shadow-lg bg-white dark:bg-gray-800">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-blue-900 dark:text-blue-100">Journaux SSH</h2>
        {loading && (
          <div className="animate-pulse text-blue-600 dark:text-blue-400">
            Chargement...
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {threatData && (
        <div className="mb-8 bg-blue-50/50 dark:bg-blue-900/20 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
            Résumé des Menaces
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
              {typeof window !== 'undefined' && (
                <ReactApexChart
                  options={chartOptions}
                  series={[
                    threatData.recent_threats.filter((t: any) => t.score <= 3).length,
                    threatData.recent_threats.filter((t: any) => t.score > 3 && t.score <= 6).length,
                    threatData.recent_threats.filter((t: any) => t.score > 6).length
                  ]}
                  type="donut"
                  height={300}
                />
              )}
            </div>
            <div className="grid grid-cols-1 gap-4">
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
                <p className="text-sm text-blue-800 dark:text-blue-200">Total des Menaces</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {threatData.recent_threats.length}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
                <p className="text-sm text-blue-800 dark:text-blue-200">Menaces Actives</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {threatData.active_threats}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
                <p className="text-sm text-blue-800 dark:text-blue-200">Score Moyen</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {(threatData.recent_threats.reduce((acc: number, t: any) => acc + t.score, 0) / 
                    threatData.recent_threats.length).toFixed(1)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Horodatage
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Utilisateur
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Adresse IP
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Niveau de Menace
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {sortedLogs.map((log, index) => (
              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {log.timestamp}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {log.username}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {log.ip_address}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${getThreatLevelColor(log.threat_level)}`}>
                    {log.threat_level?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SSHLogs;
