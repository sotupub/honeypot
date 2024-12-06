import os
import json
from datetime import datetime
from typing import List, Dict, Any

class SSHLogParser:
    def __init__(self, log_dir: str):
        """Initialize SSH log parser with log directory"""
        self.log_dir = log_dir
        self.session_log_file = os.path.join(log_dir, 'ssh', 'ssh_sessions.log')
        self.command_log_file = os.path.join(log_dir, 'ssh', 'ssh_commands.log')
    
    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp to ISO format"""
        try:
            # Try parsing the timestamp and convert to ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.isoformat()
        except Exception as e:
            print(f"Error formatting timestamp: {e}")
            return timestamp

    def get_ssh_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent SSH sessions with detailed status"""
        sessions = []
        active_sessions = {}
        try:
            if os.path.exists(self.session_log_file):
                with open(self.session_log_file, 'r') as f:
                    for line in f:
                        try:
                            if 'New SSH session' in line:
                                session_data = json.loads(line.split('New SSH session: ')[1])
                                session_id = session_data.get('session_id', '')
                                timestamp = self.format_timestamp(session_data.get('timestamp', ''))
                                
                                # Store session start time
                                active_sessions[session_id] = {
                                    'timestamp': timestamp,
                                    'username': session_data.get('username', ''),
                                    'ip_address': session_data.get('ip', ''),
                                    'session_id': session_id,
                                    'status': 'active',
                                    'login_time': timestamp
                                }
                            
                            elif 'SSH session closed' in line:
                                session_data = json.loads(line.split('SSH session closed: ')[1])
                                session_id = session_data.get('session_id', '')
                                
                                if session_id in active_sessions:
                                    session = active_sessions[session_id]
                                    session['status'] = 'closed'
                                    session['logout_time'] = self.format_timestamp(session_data.get('timestamp', ''))
                                    
                                    # Calculate duration
                                    try:
                                        start_time = datetime.fromisoformat(session['login_time'].replace('Z', '+00:00'))
                                        end_time = datetime.fromisoformat(session['logout_time'].replace('Z', '+00:00'))
                                        duration = end_time - start_time
                                        session['duration'] = str(duration)
                                    except Exception as e:
                                        print(f"Error calculating session duration: {e}")
                                        session['duration'] = 'unknown'
                                    
                                    sessions.append(session)
                                    del active_sessions[session_id]
                        except Exception as e:
                            print(f"Error parsing SSH session log line: {e}")
                            continue
                
                # Add active sessions to the list
                sessions.extend(active_sessions.values())
        except Exception as e:
            print(f"Error reading SSH session log file: {e}")
        
        # Sort by timestamp descending and take most recent
        sessions.sort(key=lambda x: x['timestamp'], reverse=True)
        return sessions[:limit]
    
    def get_ssh_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent SSH commands"""
        commands = []
        try:
            if os.path.exists(self.command_log_file):
                with open(self.command_log_file, 'r') as f:
                    for line in f:
                        try:
                            # Extract command data from log line
                            if 'Command executed' in line:
                                cmd_data = json.loads(line.split('Command executed: ')[1])
                                commands.append({
                                    'timestamp': self.format_timestamp(cmd_data.get('timestamp', '')),
                                    'username': cmd_data.get('username', ''),
                                    'ip_address': cmd_data.get('ip', ''),
                                    'command': cmd_data.get('command', ''),
                                    'session_id': cmd_data.get('session_id', '')
                                })
                        except Exception as e:
                            print(f"Error parsing SSH command log line: {e}")
                            continue
        except Exception as e:
            print(f"Error reading SSH command log file: {e}")
        
        # Sort by timestamp descending and take most recent
        commands.sort(key=lambda x: x['timestamp'], reverse=True)
        return commands[:limit]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get currently active SSH sessions"""
        sessions = self.get_ssh_sessions()
        return [s for s in sessions if s['status'] == 'active']
    
    def get_ssh_stats(self) -> Dict[str, Any]:
        """Get SSH usage statistics"""
        sessions = self.get_ssh_sessions(limit=1000)  # Get more sessions for accurate stats
        commands = self.get_ssh_commands(limit=1000)
        
        # Get unique users and IPs
        unique_users = set(s['username'] for s in sessions)
        unique_ips = set(s['ip_address'] for s in sessions)
        
        # Get command statistics
        command_types = {}
        for cmd in commands:
            command = cmd['command'].split()[0] if cmd['command'] else 'unknown'
            command_types[command] = command_types.get(command, 0) + 1
        
        return {
            'total_sessions': len(sessions),
            'active_sessions': len(self.get_active_sessions()),
            'total_commands': len(commands),
            'unique_users': len(unique_users),
            'unique_ips': len(unique_ips),
            'command_types': command_types,
            'recent_commands': self.get_ssh_commands(limit=10),
            'recent_sessions': self.get_ssh_sessions(limit=10)
        }
