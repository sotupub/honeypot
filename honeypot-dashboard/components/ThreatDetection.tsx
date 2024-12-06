import { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Card } from './ui/card';
import SecurityCharts from './SecurityCharts';
import SSHLogs from './SSHLogs';
import { WaveBackground } from './ui/wave-background';

export default function ThreatDetection() {
  const [threatData, setThreatData] = useState<any>(null);
  const [bannedIPs, setBannedIPs] = useState<any[]>([]);
  const [sshLogs, setSSHLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreatData = async () => {
      try {
        // Fetch threat data
        const threatResponse = await fetch('http://localhost:5000/api/threats');
        if (!threatResponse.ok) {
          throw new Error('Failed to fetch threat data');
        }
        const threatData = await threatResponse.json();
        setThreatData(threatData);

        // Fetch banned IPs
        const bannedIPsResponse = await fetch('http://localhost:5000/api/banned-ips');
        if (!bannedIPsResponse.ok) {
          throw new Error('Failed to fetch banned IPs');
        }
        const bannedIPsData = await bannedIPsResponse.json();
        setBannedIPs(bannedIPsData.banned_ips || []);

        // Fetch SSH Logs (with 'all' type)
        const sshLogsResponse = await fetch('http://localhost:5000/api/ssh/logs?type=all');
        if (!sshLogsResponse.ok) {
          throw new Error('Failed to fetch SSH logs');
        }
        const sshLogsData = await sshLogsResponse.json();
        setSSHLogs(sshLogsData.logs || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        // Set default empty arrays to prevent undefined errors
        setBannedIPs([]);
        setSSHLogs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchThreatData();
    const interval = setInterval(fetchThreatData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-pulse text-blue-600">Chargement des données de menace...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
        Une erreur est survenue : {error}
      </div>
    );
  }

  // Safely handle banned IPs and threat data
  const safeBannedIPs = Array.isArray(bannedIPs) ? bannedIPs : [];
  const safeThreatData = threatData || { recent_threats: [], total_threats: 0 };

  return (
    <div className="min-h-screen bg-transparent p-6 relative overflow-hidden">
      {/* Ocean-inspired Wave Background */}
      <div className="absolute inset-0 z-0 opacity-20">
        <div className="absolute top-0 left-0 w-full h-full bg-transparent  animate-wave-slow"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-transparent animate-wave-medium opacity-50 mix-blend-overlay"></div>
      </div>

      {/* Glass Morphic Container */}
      <div className="relative z-10 container mx-auto bg-white/20 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/30 overflow-hidden">
        {/* Header with Glassmorphic Design */}
        <div className="p-6 bg-white/10 backdrop-blur-sm border-b border-white/20">
          <h1 className="text-3xl font-bold mb-2 text-blue-900 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-cyan-500">
            Tableau de Bord de Sécurité du Honeypot
          </h1>
          <p className="text-sm text-blue-800/70">Surveillance et Analyse des Menaces en Temps Réel</p>
        </div>

        {/* Content Sections with Glassmorphic Cards */}
        <div className="p-6 space-y-6">
          {/* Threat Summary Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-blue-900">
                Résumé des Menaces
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-blue-800">Total des Menaces</span>
                  <span className="font-bold text-blue-900">
                    {safeThreatData.total_threats || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-800">Menaces Récentes</span>
                  <span className="font-bold text-blue-900">
                    {safeThreatData.recent_threats?.length || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Banned IPs Card */}
            <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-lg">
              <h2 className="text-2xl font-bold mb-4 text-blue-900">
                Adresses IP Bloquées
              </h2>
              {safeBannedIPs.length === 0 ? (
                <p className="text-blue-800 text-center">
                  Aucune adresse IP bloquée
                </p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {safeBannedIPs.map((ip, index) => (
                    <div 
                      key={index} 
                      className="flex justify-between items-center bg-red-500/10 p-2 rounded"
                    >
                      <span className="text-red-800">{ip.ip}</span>
                      <span className="text-xs text-blue-700">
                        Bloqué {formatDistanceToNow(new Date(ip.banned_at), { addSuffix: true, locale: 'fr' })}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Security Charts Section */}
          <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-blue-900">Aperçu des Menaces</h2>
            <SecurityCharts 
              threatData={safeThreatData} 
              bannedIPs={safeBannedIPs} 
            />
          </div>

          {/* SSH Logs Section */}
          <div className="col-span-12">
            <h2 className="text-xl font-semibold mb-4 text-blue-900">Analyse des Journaux SSH</h2>
            <SSHLogs logs={sshLogs} />
          </div>

          {/* Banned IPs Detailed List */}
          <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-lg">
            <h3 className="text-xl font-semibold mb-4 text-blue-900">
              Adresses IP Bloquées
            </h3>
            {safeBannedIPs.length === 0 ? (
              <p className="text-blue-800/70">Aucune IP bloquée actuellement</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-white/30">
                      <th className="p-3 text-blue-900">Adresse IP</th>
                      <th className="p-3 text-blue-900">Bloquée le</th>
                      <th className="p-3 text-blue-900">Raison</th>
                      <th className="p-3 text-blue-900">Expire le</th>
                    </tr>
                  </thead>
                  <tbody>
                    {safeBannedIPs.map((bannedIP, index) => (
                      <tr 
                        key={index} 
                        className="border-b border-white/20 hover:bg-white/10 transition-colors"
                      >
                        <td className="p-3 text-blue-900">{bannedIP.ip}</td>
                        <td className="p-3 text-blue-800">
                          Il y a {formatDistanceToNow(new Date(bannedIP.banned_at), { addSuffix: true, locale: 'fr' })}
                        </td>
                        <td className="p-3 text-blue-800">{bannedIP.reason}</td>
                        <td className="p-3 text-blue-800">
                          Expire {formatDistanceToNow(new Date(bannedIP.expires), { addSuffix: true, locale: 'fr' })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
