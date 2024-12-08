'use client';

import { useState } from 'react';

interface Settings {
  ssh_port: number;
  auto_ban_threshold: number;
  ban_duration: number;
  log_rotation_days: number;
  alert_email: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    ssh_port: 2222,
    auto_ban_threshold: 5,
    ban_duration: 24,
    log_rotation_days: 7,
    alert_email: '',
  });

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://57.129.78.111:5000/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      setError('Failed to save settings. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Honeypot Settings</h1>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold mb-4">General Settings</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              SSH Port
            </label>
            <input
              type="number"
              value={settings.ssh_port}
              onChange={(e) =>
                setSettings({ ...settings, ssh_port: parseInt(e.target.value) })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Auto-Ban Threshold (number of attempts)
            </label>
            <input
              type="number"
              value={settings.auto_ban_threshold}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  auto_ban_threshold: parseInt(e.target.value),
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Ban Duration (hours)
            </label>
            <input
              type="number"
              value={settings.ban_duration}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  ban_duration: parseInt(e.target.value),
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold mb-4">Logging Settings</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Log Rotation (days)
            </label>
            <input
              type="number"
              value={settings.log_rotation_days}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  log_rotation_days: parseInt(e.target.value),
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Alert Email
            </label>
            <input
              type="email"
              value={settings.alert_email}
              onChange={(e) =>
                setSettings({ ...settings, alert_email: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        {saved && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            Settings saved successfully!
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Save Settings
          </button>
        </div>
      </form>
    </div>
  );
}
