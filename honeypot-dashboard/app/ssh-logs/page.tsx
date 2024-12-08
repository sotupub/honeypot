'use client';

import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function SSHLogsPage() {
  const [sshLogs, setSSHLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSSHLogs = async () => {
      try {
        const response = await fetch('http://57.129.78.111:5000/api/ssh/logs');
        if (!response.ok) {
          throw new Error('Échec de la récupération des journaux SSH');
        }
        const data = await response.json();
        setSSHLogs(data.logs || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    };

    fetchSSHLogs();
    const interval = setInterval(fetchSSHLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-pulse text-blue-600">Chargement des journaux SSH...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-100 p-6 relative overflow-hidden">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-blue-900 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-cyan-500">
          Journaux des Sessions SSH
        </h1>

        {sshLogs.length === 0 ? (
          <div className="text-center text-blue-800 py-6">
            Aucun journal SSH disponible
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full bg-white/20 backdrop-blur-xl rounded-2xl border border-white/30">
              <thead>
                <tr className="bg-white/30">
                  <th className="p-3 text-left text-blue-900">Horodatage</th>
                  <th className="p-3 text-left text-blue-900">Nom d'Utilisateur</th>
                  <th className="p-3 text-left text-blue-900">Adresse IP</th>
                  <th className="p-3 text-left text-blue-900">Commande</th>
                  <th className="p-3 text-left text-blue-900">Statut</th>
                </tr>
              </thead>
              <tbody>
                {sshLogs.map((log, index) => (
                  <tr 
                    key={index} 
                    className="border-b border-white/20 hover:bg-white/10 transition-colors"
                  >
                    <td className="p-3 text-blue-800">
                      {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true, locale: fr })}
                    </td>
                    <td className="p-3 text-blue-800">{log.username || 'Inconnu'}</td>
                    <td className="p-3 text-blue-800">{log.ip_address || 'Inconnu'}</td>
                    <td className="p-3 text-blue-800">
                      {log.command ? (
                        <code className="bg-blue-100/50 px-2 py-1 rounded text-xs">
                          {log.command}
                        </code>
                      ) : (
                        <span className="text-blue-500 text-xs">Aucune commande</span>
                      )}
                    </td>
                    <td className="p-3">
                      <span 
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          log.status === 'success' 
                            ? 'bg-green-500/20 text-green-800' 
                            : 'bg-red-500/20 text-red-800'
                        }`}
                      >
                        {log.status === 'success' ? 'Succès' : 'Échec'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
