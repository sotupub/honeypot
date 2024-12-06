import re
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import ipaddress
from config import DATABASE_FILE

class IntrusionDetectionSystem:
    def __init__(self):
        # Configuration des seuils de détection
        self.thresholds = {
            'ssh_attempts': 5,  # Nombre max de tentatives SSH par IP en 5 minutes
            'port_scan': 10,    # Nombre max de ports scannés par IP en 1 minute
            'suspicious_commands': [
                'rm -rf',       # Commandes potentiellement dangereuses
                'wget',
                'curl',
                '/etc/shadow',
                '/etc/passwd',
                'nc',
                'netcat',
                'chmod 777',
                'base64',
            ],
            'blacklisted_ips': set()  # IPs connues comme malveillantes
        }
        
        # Dictionnaire pour suivre les tentatives
        self.attempts = defaultdict(list)
        self.load_blacklisted_ips()

    def load_blacklisted_ips(self):
        """Charger les IPs blacklistées depuis la base de données"""
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        cur.execute('SELECT ip_address FROM blocked_ips')
        self.thresholds['blacklisted_ips'] = set(ip[0] for ip in cur.fetchall())
        conn.close()

    def analyze_ssh_attempt(self, ip_address, username, timestamp):
        """Analyser une tentative de connexion SSH"""
        current_time = timestamp if timestamp else datetime.now()
        
        # Nettoyer les anciennes tentatives (plus de 5 minutes)
        self.attempts['ssh'][ip_address] = [
            attempt for attempt in self.attempts['ssh'][ip_address]
            if current_time - attempt < timedelta(minutes=5)
        ]
        
        # Ajouter la nouvelle tentative
        self.attempts['ssh'][ip_address].append(current_time)
        
        # Vérifier si le seuil est dépassé
        if len(self.attempts['ssh'][ip_address]) > self.thresholds['ssh_attempts']:
            return {
                'detected': True,
                'type': 'SSH Brute Force',
                'details': f'Plus de {self.thresholds["ssh_attempts"]} tentatives en 5 minutes'
            }
            
        return {'detected': False}

    def analyze_port_scan(self, ip_address, ports, timestamp):
        """Analyser une tentative de scan de ports"""
        current_time = timestamp if timestamp else datetime.now()
        
        # Nettoyer les anciennes tentatives (plus d'une minute)
        self.attempts['ports'][ip_address] = [
            attempt for attempt in self.attempts['ports'][ip_address]
            if current_time - attempt < timedelta(minutes=1)
        ]
        
        # Ajouter les nouvelles tentatives
        self.attempts['ports'][ip_address].extend([current_time] * len(ports))
        
        # Vérifier si le seuil est dépassé
        if len(self.attempts['ports'][ip_address]) > self.thresholds['port_scan']:
            return {
                'detected': True,
                'type': 'Port Scan',
                'details': f'Scan de {len(ports)} ports en moins d\'une minute'
            }
            
        return {'detected': False}

    def analyze_command(self, ip_address, command):
        """Analyser une commande SSH exécutée"""
        if not command:
            return {'detected': False}
            
        for suspicious in self.thresholds['suspicious_commands']:
            if suspicious in command.lower():
                return {
                    'detected': True,
                    'type': 'Suspicious Command',
                    'details': f'Commande suspecte détectée: {suspicious}'
                }
                
        return {'detected': False}

    def is_ip_suspicious(self, ip_address):
        """Vérifier si une IP est suspecte"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Vérifier si l'IP est dans la liste noire
            if ip_address in self.thresholds['blacklisted_ips']:
                return True
                
            # Vérifier si c'est une IP privée
            if ip.is_private:
                return False
                
            # Autres vérifications peuvent être ajoutées ici
            
            return False
        except ValueError:
            return True  # IP invalide est considérée comme suspecte

    def add_to_blacklist(self, ip_address, reason):
        """Ajouter une IP à la liste noire"""
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        
        try:
            cur.execute('''
                INSERT INTO blocked_ips (ip_address, reason)
                VALUES (?, ?)
                ON CONFLICT(ip_address) DO UPDATE SET
                    reason = reason || '; ' || excluded.reason,
                    timestamp = CURRENT_TIMESTAMP
            ''', (ip_address, reason))
            
            conn.commit()
            self.thresholds['blacklisted_ips'].add(ip_address)
            
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout à la liste noire: {e}")
            
        finally:
            conn.close()

    def get_attack_statistics(self):
        """Obtenir des statistiques sur les attaques"""
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        
        stats = {
            'total_attacks': 0,
            'attack_types': defaultdict(int),
            'top_attackers': [],
            'recent_attacks': []
        }
        
        try:
            # Total des attaques
            cur.execute('SELECT COUNT(*) FROM attacks')
            stats['total_attacks'] = cur.fetchone()[0]
            
            # Types d'attaques
            cur.execute('''
                SELECT attack_type, COUNT(*) 
                FROM attacks 
                GROUP BY attack_type
            ''')
            for attack_type, count in cur.fetchall():
                stats['attack_types'][attack_type] = count
            
            # Top attaquants
            cur.execute('''
                SELECT ip_address, COUNT(*) as attack_count
                FROM attacks
                GROUP BY ip_address
                ORDER BY attack_count DESC
                LIMIT 5
            ''')
            stats['top_attackers'] = cur.fetchall()
            
            # Attaques récentes
            cur.execute('''
                SELECT timestamp, ip_address, attack_type
                FROM attacks
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            stats['recent_attacks'] = cur.fetchall()
            
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            
        finally:
            conn.close()
            
        return stats

class IDSSystem:
    def __init__(self):
        self.attack_patterns = {
            'ssh_brute_force': r'Failed password for .* from (\d+\.\d+\.\d+\.\d+)',
            'port_scan': r'Port scan detected from (\d+\.\d+\.\d+\.\d+)',
            'suspicious_command': r'(rm -rf|wget|curl|nc|netcat|chmod \+x)'
        }
        
        self.attack_thresholds = {
            'ssh_attempts': 5,  # Number of failed attempts before blocking
            'scan_ports': 10,   # Number of ports scanned before blocking
            'time_window': 300  # Time window in seconds (5 minutes)
        }
        
        self.ip_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.attack_stats = {
            'total_attacks': 0,
            'blocked_ips': 0,
            'attack_types': defaultdict(int)
        }

    def analyze_attack(self, ip_address, attack_type):
        """Analyze an attack and determine if action should be taken"""
        timestamp = datetime.now()
        self.attack_stats['total_attacks'] += 1
        self.attack_stats['attack_types'][attack_type] += 1
        
        # Clean old attempts
        self._clean_old_attempts()
        
        # Record this attempt
        self.ip_attempts[ip_address].append({
            'timestamp': timestamp,
            'type': attack_type
        })
        
        # Check if IP is already blocked
        if ip_address in self.blocked_ips:
            return {
                'action': 'block',
                'reason': 'IP already blocked',
                'details': f'IP {ip_address} is in the blocklist'
            }
        
        # Analyze based on attack type
        if attack_type == 'ssh_brute_force':
            return self._analyze_ssh_attempts(ip_address)
        elif attack_type == 'port_scan':
            return self._analyze_port_scan(ip_address)
        elif attack_type == 'suspicious_command':
            return self._analyze_suspicious_command(ip_address)
        else:
            return {
                'action': 'monitor',
                'reason': 'Unknown attack type',
                'details': f'Attack type {attack_type} not recognized'
            }

    def _analyze_ssh_attempts(self, ip_address):
        """Analyze SSH brute force attempts"""
        recent_attempts = self._get_recent_attempts(ip_address, 'ssh_brute_force')
        
        if len(recent_attempts) >= self.attack_thresholds['ssh_attempts']:
            self._block_ip(ip_address, 'Multiple failed SSH attempts')
            return {
                'action': 'block',
                'reason': 'SSH brute force detected',
                'details': f'Blocked after {len(recent_attempts)} failed attempts'
            }
        
        return {
            'action': 'monitor',
            'reason': 'SSH attempts under threshold',
            'details': f'{len(recent_attempts)} failed attempts in time window'
        }

    def _analyze_port_scan(self, ip_address):
        """Analyze port scanning activity"""
        recent_scans = self._get_recent_attempts(ip_address, 'port_scan')
        
        if len(recent_scans) >= self.attack_thresholds['scan_ports']:
            self._block_ip(ip_address, 'Port scanning activity')
            return {
                'action': 'block',
                'reason': 'Port scan detected',
                'details': f'Blocked after scanning {len(recent_scans)} ports'
            }
        
        return {
            'action': 'monitor',
            'reason': 'Port scans under threshold',
            'details': f'{len(recent_scans)} ports scanned in time window'
        }

    def _analyze_suspicious_command(self, ip_address):
        """Analyze suspicious command execution"""
        recent_commands = self._get_recent_attempts(ip_address, 'suspicious_command')
        
        if len(recent_commands) > 0:
            self._block_ip(ip_address, 'Suspicious command execution')
            return {
                'action': 'block',
                'reason': 'Suspicious command detected',
                'details': 'Immediate block due to suspicious command'
            }
        
        return {
            'action': 'monitor',
            'reason': 'Command logged for analysis',
            'details': 'Command will be analyzed for patterns'
        }

    def _get_recent_attempts(self, ip_address, attack_type):
        """Get recent attempts for an IP within the time window"""
        cutoff_time = datetime.now() - timedelta(seconds=self.attack_thresholds['time_window'])
        return [
            attempt for attempt in self.ip_attempts[ip_address]
            if attempt['timestamp'] >= cutoff_time and attempt['type'] == attack_type
        ]

    def _clean_old_attempts(self):
        """Clean up old attempts outside the time window"""
        cutoff_time = datetime.now() - timedelta(seconds=self.attack_thresholds['time_window'])
        for ip in list(self.ip_attempts.keys()):
            self.ip_attempts[ip] = [
                attempt for attempt in self.ip_attempts[ip]
                if attempt['timestamp'] >= cutoff_time
            ]
            if not self.ip_attempts[ip]:
                del self.ip_attempts[ip]

    def _block_ip(self, ip_address, reason):
        """Add an IP to the blocklist"""
        if ip_address not in self.blocked_ips:
            self.blocked_ips.add(ip_address)
            self.attack_stats['blocked_ips'] += 1

    def get_statistics(self):
        """Get current IDS statistics"""
        return {
            'total_attacks': self.attack_stats['total_attacks'],
            'blocked_ips': self.attack_stats['blocked_ips'],
            'attack_types': dict(self.attack_stats['attack_types']),
            'active_threats': len(self.ip_attempts),
            'recent_activity': {
                ip: len(attempts) for ip, attempts in self.ip_attempts.items()
            }
        }
