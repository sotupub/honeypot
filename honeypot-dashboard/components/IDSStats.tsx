import { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface IDSStats {
  total_attacks: number;
  attack_types: { [key: string]: number };
  top_attackers: [string, number][];
  recent_attacks: [string, string, string][];
}

const IDSStats = () => {
  const [stats, setStats] = useState<IDSStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://57.129.78.111:5000/api/ids/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Error fetching IDS stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !stats) {
    return (
      <div className="glass-card p-6 animate-pulse">
        <div className="h-64 bg-blue-200/20 rounded"></div>
      </div>
    );
  }

  // Préparer les données pour le graphique
  const chartData = {
    labels: Object.keys(stats.attack_types),
    datasets: [
      {
        data: Object.values(stats.attack_types),
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <h2 className="text-xl font-bold text-blue-100 mb-4">
        Système de Détection d'Intrusion
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Graphique des types d'attaques */}
        <div className="bg-slate-800/50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-100 mb-2">
            Types d'Attaques
          </h3>
          <div className="h-64">
            <Pie data={chartData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Top Attaquants */}
        <div className="bg-slate-800/50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-100 mb-2">
            Top Attaquants
          </h3>
          <div className="space-y-2">
            {stats.top_attackers.map(([ip, count], index) => (
              <div
                key={ip}
                className="flex justify-between items-center p-2 rounded bg-slate-700/50"
              >
                <span className="text-blue-100">{ip}</span>
                <span className="text-blue-300">{count} attaques</span>
              </div>
            ))}
          </div>
        </div>

        {/* Attaques Récentes */}
        <div className="md:col-span-2 bg-slate-800/50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-100 mb-2">
            Attaques Récentes
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-blue-300">
                  <th className="p-2">Timestamp</th>
                  <th className="p-2">IP</th>
                  <th className="p-2">Type</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_attacks.map(([timestamp, ip, type], index) => (
                  <tr
                    key={index}
                    className="border-t border-slate-700/50 text-blue-100"
                  >
                    <td className="p-2">{new Date(timestamp).toLocaleString()}</td>
                    <td className="p-2">{ip}</td>
                    <td className="p-2">{type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IDSStats;
