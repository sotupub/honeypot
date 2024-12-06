'use client';

import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function AttacksPage() {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAttacks = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/attacks');
        if (!response.ok) {
          throw new Error('Échec de la récupération des données d\'attaques');
        }
        const data = await response.json();
        setAttacks(data.attacks || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    };

    fetchAttacks();
    const interval = setInterval(fetchAttacks, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-pulse text-blue-600">Chargement des attaques...</div>
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
          Détection et Analyse des Attaques
        </h1>

        {attacks.length === 0 ? (
          <div className="text-center text-blue-800 py-6">
            Aucune attaque détectée
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {attacks.map((attack, index) => (
              <div 
                key={index} 
                className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-lg"
              >
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-blue-900">
                    Attaque {index + 1}
                  </h3>
                  <span 
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      attack.severity === 'high' 
                        ? 'bg-red-500/20 text-red-800' 
                        : attack.severity === 'medium' 
                        ? 'bg-yellow-500/20 text-yellow-800' 
                        : 'bg-green-500/20 text-green-800'
                    }`}
                  >
                    {attack.severity === 'high' 
                      ? 'Risque Élevé' 
                      : attack.severity === 'medium' 
                      ? 'Risque Moyen' 
                      : 'Risque Faible'}
                  </span>
                </div>
                <div className="space-y-2 text-blue-800">
                  <p>
                    <strong>Adresse IP:</strong> {attack.ip_address}
                  </p>
                  <p>
                    <strong>Type d'Attaque:</strong> {attack.attack_type}
                  </p>
                  <p>
                    <strong>Détectée:</strong> {formatDistanceToNow(new Date(attack.timestamp), { addSuffix: true, locale: fr })}
                  </p>
                  <p>
                    <strong>Score de Menace:</strong> {attack.threat_score}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
