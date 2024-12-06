import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import json

class LogParser:
    def __init__(self, log_dir: str):
        """Initialize the log parser with the directory containing log files"""
        self.log_dir = log_dir
        
        # Regular expressions for different log patterns
        self.patterns = {
            'ssh_auth': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+(?P<message>.*?)(\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+))?',
            'ssh_connection': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+Connection\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+)',
            'ssh_invalid': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+Invalid\s+user\s+(?P<username>\S+)\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+)',
            'ssh_failed': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+Failed\s+password\s+for\s+(invalid\s+user\s+)?(?P<username>\S+)\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+)',
            'ssh_accepted': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+Accepted\s+password\s+for\s+(?P<username>\S+)\s+from\s+(?P<ip>\d+\.\d+\.\d+\.\d+)',
        }
        
        # Compile regular expressions
        self.compiled_patterns = {
            name: re.compile(pattern) for name, pattern in self.patterns.items()
        }
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Convert log timestamp to datetime object"""
        try:
            current_year = datetime.now().year
            return datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
        except ValueError as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            return datetime.now()
    
    def classify_attack(self, log_entry: Dict[str, Any]) -> str:
        """Classify the type of attack based on log entry"""
        message = log_entry.get('message', '').lower()
        
        if 'invalid user' in message:
            return 'ssh_brute_force'
        elif 'failed password' in message:
            return 'ssh_brute_force'
        elif 'connection closed by authenticating user' in message:
            return 'ssh_scan'
        elif 'did not receive identification string' in message:
            return 'port_scan'
        elif 'possible break-in attempt' in message:
            return 'suspicious_activity'
        elif 'bad protocol version identification' in message:
            return 'protocol_violation'
        else:
            return 'other'
    
    def parse_log_file(self, filename: str) -> List[Dict[str, Any]]:
        """Parse a single log file and return list of parsed entries"""
        entries = []
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self.parse_log_line(line)
                    if entry:
                        entries.append(entry)
        except Exception as e:
            print(f"Error reading log file {filename}: {e}")
        
        return entries
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Parse a single log line and return structured data"""
        for pattern_name, pattern in self.compiled_patterns.items():
            match = pattern.search(line)
            if match:
                data = match.groupdict()
                if 'timestamp' in data:
                    data['timestamp'] = self.parse_timestamp(data['timestamp'])
                data['type'] = pattern_name
                data['attack_type'] = self.classify_attack({'message': line})
                data['raw_message'] = line.strip()
                return data
        return None
    
    def get_recent_attacks(self, limit: int = 10) -> List[Tuple[str, str, str]]:
        """Get recent attacks from logs"""
        attacks = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith('auth.log') or filename.startswith('secure'):
                entries = self.parse_log_file(filename)
                for entry in entries:
                    if entry and 'timestamp' in entry and 'ip' in entry:
                        attacks.append((
                            entry['timestamp'].isoformat(),
                            entry['ip'],
                            entry['attack_type']
                        ))
        
        # Sort by timestamp descending and take most recent
        attacks.sort(reverse=True)
        return attacks[:limit]
    
    def get_attack_stats(self) -> Dict[str, Any]:
        """Get statistics about attacks from logs"""
        stats = {
            'total_attacks': 0,
            'attack_types': {},
            'top_attackers': {},
            'recent_attacks': []
        }
        
        for filename in os.listdir(self.log_dir):
            if filename.startswith('auth.log') or filename.startswith('secure'):
                entries = self.parse_log_file(filename)
                for entry in entries:
                    if entry and 'attack_type' in entry:
                        stats['total_attacks'] += 1
                        
                        # Count attack types
                        attack_type = entry['attack_type']
                        stats['attack_types'][attack_type] = stats['attack_types'].get(attack_type, 0) + 1
                        
                        # Count attacks per IP
                        if 'ip' in entry:
                            ip = entry['ip']
                            stats['top_attackers'][ip] = stats['top_attackers'].get(ip, 0) + 1
        
        # Convert top_attackers to sorted list of tuples
        top_attackers = sorted(
            stats['top_attackers'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        stats['top_attackers'] = top_attackers
        
        # Get recent attacks
        stats['recent_attacks'] = self.get_recent_attacks()
        
        return stats
