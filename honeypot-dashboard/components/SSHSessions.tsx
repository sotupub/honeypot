'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { formatDistanceToNow, isValid } from 'date-fns';

interface SSHSession {
  timestamp: string;
  username: string;
  ip_address: string;
  session_id: string;
  status: 'active' | 'closed';
  duration?: string;
  login_time?: string;
  logout_time?: string;
}

export default function SSHSessions() {
  const [sessions, setSessions] = useState<SSHSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/ssh/sessions');
        if (!response.ok) throw new Error('Failed to fetch SSH sessions');
        const data = await response.json();
        setSessions(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch SSH sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
    const interval = setInterval(fetchSessions, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Badge variant="success">Active</Badge>;
      case 'closed':
        return <Badge variant="secondary">Closed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

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

  const formatDuration = (session: SSHSession) => {
    if (session.status === 'active') {
      const loginTime = session.login_time ? new Date(session.login_time) : null;
      if (!loginTime || !isValid(loginTime)) return '-';
      try {
        return formatDistanceToNow(loginTime);
      } catch (error) {
        console.error('Error calculating duration:', error);
        return '-';
      }
    }
    return session.duration || '-';
  };

  if (loading) return <div>Loading SSH sessions...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>SSH Sessions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>Login Time</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sessions.map((session, index) => (
              <TableRow key={session.session_id || index}>
                <TableCell className="font-medium">{session.username}</TableCell>
                <TableCell>{session.ip_address}</TableCell>
                <TableCell>{formatDate(session.login_time || session.timestamp)}</TableCell>
                <TableCell>{formatDuration(session)}</TableCell>
                <TableCell>{getStatusBadge(session.status)}</TableCell>
              </TableRow>
            ))}
            {sessions.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No active SSH sessions
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
