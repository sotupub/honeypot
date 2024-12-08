'use client';

import { useEffect, useState } from 'react';
import StatsCard from '../components/StatsCard';
import AttackTable from '../components/AttackTable';
import SSHLogs from '../components/SSHLogs';
import IDSStats from '../components/IDSStats';
import AdvancedAnalysis from '../components/AdvancedAnalysis';
import SSHActivity from '../components/SSHActivity';
import SSHSessions from '../components/SSHSessions';
import ThreatDetection from '@/components/ThreatDetection';

interface DashboardData {
  stats: {
    total_attacks: number;
    active_sessions: number;
    blocked_ips: number;
    unique_attackers: number;
  };
  recent_attacks: {
    timestamp: string;
    ip_address: string;
    attack_type: string;
    status: string;
  }[];
  ssh_logs: {
    timestamp: string;
    username: string;
    ip_address: string;
    command: string;
    session_id: string;
  }[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://57.129.78.111:5000/api/dashboard');
        if (!response.ok) throw new Error('Failed to fetch dashboard data');
        const jsonData = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Chargement du tableau de bord...</div>;
  if (error) return <div>Erreur : {error}</div>;
  if (!data) return null;

    return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Tableau de Bord de Sécurité du Honeypot</h2>
      </div>
      <div className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Total des Attaques"
            value={data.stats.total_attacks}
            description="Total des attaques détectées"
          />
          <StatsCard
            title="Sessions Actives"
            value={data.stats.active_sessions}
            description="Sessions SSH actuelles"
          />
          <StatsCard
            title="IP Bloqués"
            value={data.stats.blocked_ips}
            description="IP bloqués pour activité suspecte"
          />
          <StatsCard
            title="Attaquants Uniques"
            value={data.stats.unique_attackers}
            description="IP attaquants distincts"
          />
        </div>

       

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          
          <div className="col-span-12">
        <SSHActivity />
      </div>
      </div>

        {/* Add SSH Sessions component */}
        <SSHSessions />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="col-span-12">
          <SSHLogs logs={data.ssh_logs} />
          </div>
        </div>

       
      </div>
    </div>
  );
}
