'use client';

import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface AnalysisReport {
  timestamp: string;
  summary: {
    total_attacks: number;
    unique_ips: number;
    blocked_ips: number;
    anomalies_detected: number;
  };
  patterns: {
    temporal: {
      peak_hours: { [key: string]: number };
      busiest_days: { [key: string]: number };
    };
    attack_types: {
      distribution: { [key: string]: number };
      success_rate: number;
    };
    geographic?: {
      top_countries: { [key: string]: number };
      attack_by_region: { [key: string]: { [key: string]: number } };
    };
    anomalies: {
      count: number;
      percentage: number;
    };
    clusters: {
      count: number;
      distribution: { [key: string]: number };
    };
  };
  high_risk_ips: Array<{
    ip: string;
    threat_score: number;
    attack_count: number;
    attack_types: string[];
  }>;
}

const defaultReport: AnalysisReport = {
  timestamp: new Date().toISOString(),
  summary: {
    total_attacks: 0,
    unique_ips: 0,
    blocked_ips: 0,
    anomalies_detected: 0,
  },
  patterns: {
    temporal: {
      peak_hours: {},
      busiest_days: {},
    },
    attack_types: {
      distribution: {},
      success_rate: 0,
    },
    anomalies: {
      count: 0,
      percentage: 0,
    },
    clusters: {
      count: 0,
      distribution: {},
    },
  },
  high_risk_ips: [],
};

const AdvancedAnalysis = () => {
  const [report, setReport] = useState<AnalysisReport>(defaultReport);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch('http://57.129.78.111:5000/api/analysis/full');
        if (!response.ok) {
          throw new Error('Failed to fetch analysis data');
        }
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        setReport(data);
        setError(null);
      } catch (error) {
        console.error('Error fetching analysis:', error);
        setError(error instanceof Error ? error.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="glass-card p-6 animate-pulse">
        <div className="h-64 bg-blue-200/20 rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6">
        <div className="text-red-400 text-center">
          <h3 className="text-lg font-semibold mb-2">Error Loading Analysis</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Préparer les données pour le graphique temporel
  const temporalData = {
    labels: Object.keys(report.patterns.temporal.peak_hours || {}),
    datasets: [
      {
        label: 'Attaques par heure',
        data: Object.values(report.patterns.temporal.peak_hours || {}),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  // Préparer les données pour le graphique des types d'attaque
  const attackTypesData = {
    labels: Object.keys(report.patterns.attack_types.distribution || {}),
    datasets: [
      {
        data: Object.values(report.patterns.attack_types.distribution || {}),
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
        ],
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold text-blue-100 mb-4">
          Analyse Avancée des Intrusions
        </h2>

        {/* Résumé */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-300">Total Attaques</h3>
            <p className="text-2xl font-bold text-blue-100">
              {report.summary.total_attacks}
            </p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-300">IPs Uniques</h3>
            <p className="text-2xl font-bold text-blue-100">
              {report.summary.unique_ips}
            </p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-300">Anomalies</h3>
            <p className="text-2xl font-bold text-blue-100">
              {report.summary.anomalies_detected}
            </p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-300">Taux de Blocage</h3>
            <p className="text-2xl font-bold text-blue-100">
              {report.summary.unique_ips > 0
                ? ((report.summary.blocked_ips / report.summary.unique_ips) * 100).toFixed(1)
                : '0'}%
            </p>
          </div>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {Object.keys(report.patterns.temporal.peak_hours || {}).length > 0 && (
            <div className="bg-slate-800/50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-100 mb-2">
                Distribution Temporelle
              </h3>
              <Line
                data={temporalData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      display: true,
                      labels: { color: '#93c5fd' },
                    },
                  },
                  scales: {
                    y: {
                      ticks: { color: '#93c5fd' },
                      grid: { color: 'rgba(147, 197, 253, 0.1)' },
                    },
                    x: {
                      ticks: { color: '#93c5fd' },
                      grid: { color: 'rgba(147, 197, 253, 0.1)' },
                    },
                  },
                }}
              />
            </div>
          )}

          {Object.keys(report.patterns.attack_types.distribution || {}).length > 0 && (
            <div className="bg-slate-800/50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-100 mb-2">
                Types d'Attaques
              </h3>
              <Pie
                data={attackTypesData}
                options={{
                  plugins: {
                    legend: {
                      display: true,
                      position: 'right' as const,
                      labels: { color: '#93c5fd' },
                    },
                  },
                }}
              />
            </div>
          )}
        </div>

        {/* IPs à Haut Risque */}
        {report.high_risk_ips.length > 0 && (
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-100 mb-2">
              IPs à Haut Risque
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-blue-300">
                    <th className="p-2">IP</th>
                    <th className="p-2">Score de Menace</th>
                    <th className="p-2">Nombre d'Attaques</th>
                    <th className="p-2">Types d'Attaques</th>
                  </tr>
                </thead>
                <tbody>
                  {report.high_risk_ips.map((ip) => (
                    <tr
                      key={ip.ip}
                      className="border-t border-slate-700/50 text-blue-100"
                    >
                      <td className="p-2">{ip.ip}</td>
                      <td className="p-2">
                        <div className="flex items-center">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-green-500 to-red-500"
                            style={{ width: `${ip.threat_score}%` }}
                          />
                          <span className="ml-2">{ip.threat_score.toFixed(1)}</span>
                        </div>
                      </td>
                      <td className="p-2">{ip.attack_count}</td>
                      <td className="p-2">
                        {ip.attack_types.join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Informations Géographiques */}
        {report.patterns.geographic && Object.keys(report.patterns.geographic.top_countries || {}).length > 0 && (
          <div className="bg-slate-800/50 p-4 rounded-lg mt-6">
            <h3 className="text-lg font-semibold text-blue-100 mb-2">
              Distribution Géographique
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-semibold text-blue-300 mb-2">
                  Top 5 Pays
                </h4>
                <div className="space-y-2">
                  {Object.entries(report.patterns.geographic.top_countries).map(
                    ([country, count]) => (
                      <div
                        key={country}
                        className="flex justify-between items-center p-2 rounded bg-slate-700/50"
                      >
                        <span className="text-blue-100">{country}</span>
                        <span className="text-blue-300">{count} attaques</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedAnalysis;
