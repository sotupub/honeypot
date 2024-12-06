'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { formatDistanceToNow, isValid } from 'date-fns';

interface SSHCommand {
  timestamp: string;
  username: string;
  ip_address: string;
  command: string;
  session_id: string;
}

interface SSHSession {
  timestamp: string;
  username: string;
  ip_address: string;
  session_id: string;
  status: string;
}

interface SSHStats {
  total_sessions: number;
  active_sessions: number;
  total_commands: number;
  unique_users: number;
  unique_ips: number;
  command_types: Record<string, number>;
  recent_commands: SSHCommand[];
  recent_sessions: SSHSession[];
}

export default function SSHActivity() {
  const [sshStats, setSSHStats] = useState<SSHStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSSHStats = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/ssh/stats');
        if (!response.ok) throw new Error('Failed to fetch SSH stats');
        const data = await response.json();
        setSSHStats(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch SSH stats');
      } finally {
        setLoading(false);
      }
    };

    fetchSSHStats();
    const interval = setInterval(fetchSSHStats, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    if (!isValid(date)) return 'Invalid date';
    try {
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateStr;
    }
  };

  if (loading) return <div>Loading SSH activity...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!sshStats) return null;

  return (
    <div className="grid gap-4">
      {/* SSH Overview Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sshStats.active_sessions}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Commands</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sshStats.total_commands}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sshStats.unique_users}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique IPs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sshStats.unique_ips}</div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Commands Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent SSH Commands</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>User</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Command</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sshStats.recent_commands.map((cmd, index) => (
                <TableRow key={index}>
                  <TableCell>{formatDate(cmd.timestamp)}</TableCell>
                  <TableCell>{cmd.username}</TableCell>
                  <TableCell>{cmd.ip_address}</TableCell>
                  <TableCell>
                    <code className="bg-muted px-2 py-1 rounded">{cmd.command}</code>
                  </TableCell>
                </TableRow>
              ))}
              {sshStats.recent_commands.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    No recent commands
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Active Sessions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active SSH Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Connected</TableHead>
                <TableHead>User</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sshStats.recent_sessions
                .filter(session => session.status === 'active')
                .map((session, index) => (
                  <TableRow key={index}>
                    <TableCell>{formatDate(session.timestamp)}</TableCell>
                    <TableCell>{session.username}</TableCell>
                    <TableCell>{session.ip_address}</TableCell>
                    <TableCell>
                      <Badge variant="success">Active</Badge>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
