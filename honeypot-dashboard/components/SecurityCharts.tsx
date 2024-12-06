'use client';

import { useEffect, useState, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { Card } from './ui/card';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Ocean-inspired color palette
const OCEAN_COLORS = {
  deepBlue: 'rgba(0, 51, 102, 0.8)',
  mediumBlue: 'rgba(0, 102, 153, 0.7)',
  lightBlue: 'rgba(0, 153, 204, 0.6)',
  turquoise: 'rgba(0, 204, 204, 0.5)',
  gradient: [
    'rgba(0, 51, 102, 0.8)',
    'rgba(0, 102, 153, 0.7)',
    'rgba(0, 153, 204, 0.6)',
    'rgba(0, 204, 204, 0.5)'
  ]
};

interface SecurityChartsProps {
  threatData: any;
  bannedIPs: any[];
}

export default function SecurityCharts({ threatData, bannedIPs }: SecurityChartsProps) {
  // Attack Type Distribution
  const attackTypeData = {
    labels: threatData?.recent_threats?.map((t: any) => Object.keys(t.attack_types)[0]) || [],
    datasets: [{
      label: 'Attack Types',
      data: threatData?.recent_threats?.map((t: any) => Object.values(t.attack_types)[0]) || [],
      backgroundColor: OCEAN_COLORS.gradient,
      borderColor: OCEAN_COLORS.deepBlue,
      borderWidth: 1
    }]
  };

  // Banned IPs Over Time
  const bannedIPsData = {
    labels: bannedIPs.map(ip => new Date(ip.banned_at).toLocaleDateString()),
    datasets: [{
      label: 'Banned IPs',
      data: bannedIPs.map((_, index) => index + 1),
      borderColor: OCEAN_COLORS.mediumBlue,
      backgroundColor: OCEAN_COLORS.lightBlue,
      tension: 0.4
    }]
  };

  // Threat Severity Distribution
  const threatSeverityData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [{
      label: 'Threat Severity',
      data: [
        threatData?.recent_threats?.filter((t: any) => t.score <= 3).length || 0,
        threatData?.recent_threats?.filter((t: any) => t.score > 3 && t.score <= 6).length || 0,
        threatData?.recent_threats?.filter((t: any) => t.score > 6).length || 0
      ],
      backgroundColor: [
        'rgba(0, 204, 204, 0.5)',   // Low Risk - Turquoise
        'rgba(0, 153, 204, 0.6)',   // Medium Risk - Light Blue
        'rgba(0, 51, 102, 0.8)'     // High Risk - Deep Blue
      ]
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: OCEAN_COLORS.deepBlue
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: OCEAN_COLORS.mediumBlue
        }
      },
      x: {
        ticks: {
          color: OCEAN_COLORS.mediumBlue
        }
      }
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Attack Types Chart */}
      <Card className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 text-blue-900">Attack Types Distribution</h3>
        <Bar 
          data={attackTypeData} 
          options={{
            ...chartOptions,
            plugins: {
              ...chartOptions.plugins,
              title: {
                display: true,
                text: 'Recent Attack Types',
                color: OCEAN_COLORS.deepBlue
              }
            }
          }} 
        />
      </Card>

      {/* Banned IPs Over Time */}
      <Card className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 text-blue-900">Banned IPs Trend</h3>
        <Line 
          data={bannedIPsData} 
          options={{
            ...chartOptions,
            plugins: {
              ...chartOptions.plugins,
              title: {
                display: true,
                text: 'Cumulative Banned IPs',
                color: OCEAN_COLORS.deepBlue
              }
            }
          }} 
        />
      </Card>

      {/* Threat Severity Distribution */}
      <Card className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 text-blue-900">Threat Severity</h3>
        <Doughnut 
          data={threatSeverityData} 
          options={{
            ...chartOptions,
            plugins: {
              ...chartOptions.plugins,
              title: {
                display: true,
                text: 'Threat Risk Levels',
                color: OCEAN_COLORS.deepBlue
              }
            }
          }} 
        />
      </Card>

      {/* Additional Statistics Cards */}
      <Card className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 shadow-lg flex flex-col">
        <h3 className="text-lg font-semibold mb-4 text-blue-900">Security Overview</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-100 p-3 rounded-lg">
            <p className="text-sm text-blue-800">Total Banned IPs</p>
            <p className="text-2xl font-bold text-blue-900">{bannedIPs.length}</p>
          </div>
          <div className="bg-blue-100 p-3 rounded-lg">
            <p className="text-sm text-blue-800">Total Threats</p>
            <p className="text-2xl font-bold text-blue-900">
              {threatData?.recent_threats?.length || 0}
            </p>
          </div>
          <div className="bg-blue-100 p-3 rounded-lg">
            <p className="text-sm text-blue-800">High Risk Threats</p>
            <p className="text-2xl font-bold text-blue-900">
              {threatData?.recent_threats?.filter((t: any) => t.score > 6).length || 0}
            </p>
          </div>
          <div className="bg-blue-100 p-3 rounded-lg">
            <p className="text-sm text-blue-800">Unique Attack Types</p>
            <p className="text-2xl font-bold text-blue-900">
              {new Set(threatData?.recent_threats?.flatMap((t: any) => Object.keys(t.attack_types))).size || 0}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
