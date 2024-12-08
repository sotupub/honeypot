'use client';

import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import ThreatDetection from '@/components/ThreatDetection';
import dynamic from 'next/dynamic';

const ReactApexChart = dynamic(() => import('react-apexcharts'), { ssr: false });

export default function AttacksPage() {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Prepare chart data
  const prepareChartData = (attacks: any[]) => {
    const statusCounts = {
      blocked: attacks.filter(a => a.status === 'blocked').length,
      detected: attacks.filter(a => a.status === 'detected').length,
      attempted: attacks.filter(a => a.status === 'attempted').length
    };

    return {
      series: [statusCounts.blocked, statusCounts.detected, statusCounts.attempted],
      options: {
        chart: {
          type: 'donut',
          foreColor: '#6B7280'
        },
        labels: ['Bloquées', 'Détectées', 'Tentatives'],
        colors: ['#EF4444', '#F59E0B', '#10B981'],
        legend: {
          position: 'bottom',
          labels: {
            colors: '#6B7280'
          }
        },
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true,
                total: {
                  show: true,
                  label: 'Total des Attaques',
                  color: '#6B7280'
                }
              }
            }
          }
        },
        dataLabels: {
          enabled: true,
          formatter: function (val: number, opts: any) {
            return opts.w.config.series[opts.seriesIndex];
          }
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 300
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      }
    };
  };

  useEffect(() => {
    const fetchAttacks = async () => {
      try {
        const response = await fetch('http://57.129.78.111:5000/api/attacks');
        if (!response.ok) {
          throw new Error('Failed to fetch attack data');
        }
        const data = await response.json();
        setAttacks(data.attacks || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAttacks();
    const interval = setInterval(fetchAttacks, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  const chartData = prepareChartData(attacks);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
          Résumé des Menaces
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Surveillance en temps réel des menaces et des attaques
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Threat Detection Component */}
        <div className="col-span-1 lg:col-span-2">
          <ThreatDetection />
        </div>

        {/* Attack Statistics with Chart */}
        <div className="glass-card p-6 rounded-lg shadow-lg bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-6 text-gray-800 dark:text-white">
            Distribution des Attaques
          </h2>
          <div className="w-full" style={{ minHeight: '400px' }}>
            {typeof window !== 'undefined' && (
              <ReactApexChart
                options={chartData.options}
                series={chartData.series}
                type="donut"
                height={400}
              />
            )}
          </div>
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{attacks.length}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Bloquées</p>
              <p className="text-2xl font-bold text-red-600">{attacks.filter(a => a.status === 'blocked').length}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">IP Uniques</p>
              <p className="text-2xl font-bold text-blue-600">{new Set(attacks.map(a => a.ip_address)).size}</p>
            </div>
          </div>
        </div>

        {/* Recent Attacks List */}
        <div className="glass-card p-6 rounded-lg shadow-lg bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Attaques Récentes</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Temps
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Adresse IP
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {attacks.slice(0, 5).map((attack, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                      {formatDistanceToNow(new Date(attack.timestamp), { addSuffix: true, locale: fr })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {attack.ip_address}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                      {attack.attack_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        attack.status === 'blocked'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : attack.status === 'detected'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      }`}>
                        {attack.status === 'blocked' ? 'Bloquée' :
                         attack.status === 'detected' ? 'Détectée' : 'Tentative'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
