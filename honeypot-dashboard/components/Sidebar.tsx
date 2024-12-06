'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const Sidebar = () => {
  const pathname = usePathname();

  const menuItems = [
    { href: '/', label: 'Tableau de Bord', icon: '🌊' },
    { href: '/attacks', label: 'Attaques', icon: '⚠️' },
    { href: '/ssh-logs', label: 'Journaux SSH', icon: '🔒' },
   
  ];

  return (
    <div className="glass w-64 min-h-screen p-6 relative z-10">
      <div className="text-2xl font-bold mb-12 flex items-center space-x-3">
        <span className="text-3xl">🌊</span>
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-200 to-white">
          Garde Océanique
        </span>
      </div>
      <nav className="space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 ${
              pathname === item.href
                ? 'glass text-white'
                : 'text-blue-100 hover:glass'
            }`}
          >
            <span className="text-xl mr-3">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="absolute bottom-6 left-6 right-6">
        <div className="glass-card text-center py-4">
          <p className="text-sm text-blue-100">Moniteur Honeypot v1.0</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
