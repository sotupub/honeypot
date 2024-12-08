import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/Sidebar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Honeypot Dashboard',
  description: 'Secure monitoring system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen relative">
          <Sidebar />
          <main className="flex-1 relative z-10 p-4">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
