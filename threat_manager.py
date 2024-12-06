import sqlite3
import ipaddress
import time
from datetime import datetime, timedelta
from logger import honeypot_logger
import json
import requests
from config import *
import re

class ThreatManager:
    def __init__(self, db_file=DATABASE_FILE):
        self.db_file = db_file
        self.setup_database()
        self.banned_ips = set()
        self.attack_patterns = {}
        self.load_banned_ips()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Table pour les IP bannies
        c.execute('''CREATE TABLE IF NOT EXISTS banned_ips
                    (ip_address TEXT PRIMARY KEY,
                     ban_timestamp TEXT,
                     reason TEXT,
                     expires TEXT)''')
        
        # Table pour le scoring des menaces
        c.execute('''CREATE TABLE IF NOT EXISTS threat_scores
                    (ip_address TEXT PRIMARY KEY,
                     score INTEGER,
                     last_attack TEXT,
                     attack_count INTEGER,
                     attack_types TEXT)''')
        
        # Table pour les patterns d'attaque
        c.execute('''CREATE TABLE IF NOT EXISTS attack_patterns
                    (pattern_id TEXT PRIMARY KEY,
                     pattern_type TEXT,
                     pattern_data TEXT,
                     severity INTEGER,
                     created_at TEXT)''')
        
        # Table pour les scans de ports
        c.execute('''CREATE TABLE IF NOT EXISTS port_scans
                    (ip_address TEXT,
                     port INTEGER,
                     timestamp TEXT)''')
        
        conn.commit()
        conn.close()

    def load_banned_ips(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT ip_address FROM banned_ips WHERE expires > ?", 
                 (datetime.now().isoformat(),))
        self.banned_ips = set(ip[0] for ip in c.fetchall())
        conn.close()

    def is_ip_banned(self, ip_address):
        return ip_address in self.banned_ips

    def ban_ip(self, ip_address, reason="Multiple failed attempts", duration_hours=24):
        if ip_address in self.banned_ips:
            return False

        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now()
        expires = now + timedelta(hours=duration_hours)
        
        c.execute("""INSERT OR REPLACE INTO banned_ips 
                    (ip_address, ban_timestamp, reason, expires) 
                    VALUES (?, ?, ?, ?)""",
                 (ip_address, now.isoformat(), reason, expires.isoformat()))
        
        conn.commit()
        conn.close()
        
        self.banned_ips.add(ip_address)
        honeypot_logger.warning(f"IP {ip_address} banned for {duration_hours} hours. Reason: {reason}")
        return True

    def update_threat_score(self, ip_address, attack_type, severity=1):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Récupérer le score actuel
        c.execute("SELECT score, attack_types, attack_count FROM threat_scores WHERE ip_address = ?",
                 (ip_address,))
        result = c.fetchone()
        
        if result:
            current_score, attack_types_json, attack_count = result
            attack_types = json.loads(attack_types_json)
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
            new_score = current_score + severity
            attack_count += 1
        else:
            attack_types = {attack_type: 1}
            new_score = severity
            attack_count = 1
        
        c.execute("""INSERT OR REPLACE INTO threat_scores 
                    (ip_address, score, last_attack, attack_count, attack_types) 
                    VALUES (?, ?, ?, ?, ?)""",
                 (ip_address, new_score, datetime.now().isoformat(), 
                  attack_count, json.dumps(attack_types)))
        
        conn.commit()
        conn.close()
        
        # Vérifier si le score dépasse le seuil de bannissement
        if new_score >= BAN_THRESHOLD:
            self.ban_ip(ip_address, f"Threat score exceeded threshold: {new_score}")

    def analyze_payload(self, payload, headers):
        """Analyse le payload pour détecter des patterns d'attaque connus"""
        threats = []
        
        # Détection d'injection SQL
        sql_patterns = [
            "UNION SELECT", "OR '1'='1", "DROP TABLE",
            "'; exec", "/*", "*/", "xp_cmdshell",
            "SELECT FROM", "INSERT INTO", "DELETE FROM",
            "WAITFOR DELAY", "BENCHMARK(", "SLEEP(",
            "IF(", "CASE WHEN", "LOAD_FILE(",
            "UTL_HTTP", "DBMS_LDAP"
        ]
        if any(pattern.lower() in payload.lower() for pattern in sql_patterns):
            threats.append(("SQL_INJECTION", 5))
        
        # Détection XSS
        xss_patterns = [
            "<script>", "javascript:", "onerror=", "onload=",
            "eval(", "alert(", "document.cookie",
            "onmouseover=", "onfocus=", "onblur=",
            "expression(", "fromCharCode", "innerHTML",
            "<img src=", "<svg", "<iframe",
            "data:text/html", "vbscript:", "base64,"
        ]
        if any(pattern.lower() in payload.lower() for pattern in xss_patterns):
            threats.append(("XSS", 4))
        
        # Détection Command Injection
        cmd_patterns = [
            "|", ";", "&&", "||", "`", "$(",
            "wget ", "curl ", "nc ", "bash -i",
            "/etc/passwd", "/etc/shadow", ">/dev/null",
            ".ssh/authorized_keys", "chmod ", "chown ",
            "pkexec", "sudo ", "su -", "eval ",
            "system(", "exec(", "shell_exec(",
            "python -c", "perl -e", "ruby -e",
            "tcpdump", "wireshark", "netcat"
        ]
        if any(pattern in payload for pattern in cmd_patterns):
            threats.append(("COMMAND_INJECTION", 5))

        # Détection de Directory Traversal
        traversal_patterns = [
            "../", "..\\", "%2e%2e", "..;/",
            "..;\\", "..%00/", "..%00\\",
            "..%01/", "/etc/", "c:\\windows\\",
            "boot.ini", "web.config", ".htaccess",
            "wp-config.php", "config.php"
        ]
        if any(pattern.lower() in payload.lower() for pattern in traversal_patterns):
            threats.append(("DIRECTORY_TRAVERSAL", 4))

        # Détection de File Inclusion
        inclusion_patterns = [
            "include(", "require(", "include_once(",
            "require_once(", "fopen(", "file_get_contents(",
            "file://", "php://", "zip://", "data://",
            "expect://", "input://", "glob://"
        ]
        if any(pattern.lower() in payload.lower() for pattern in inclusion_patterns):
            threats.append(("FILE_INCLUSION", 4))
        
        # Détection de scan de ports/vulnérabilités
        if "User-Agent" in headers:
            ua = headers["User-Agent"].lower()
            scanner_patterns = [
                "nmap", "nikto", "sqlmap", "burp", "metasploit",
                "acunetix", "nessus", "openvas", "w3af", "zap",
                "dirbuster", "gobuster", "wfuzz", "hydra",
                "medusa", "brutus", "wpscan", "joomscan"
            ]
            if any(tool in ua for tool in scanner_patterns):
                threats.append(("VULNERABILITY_SCAN", 3))

        # Détection de Bruteforce SSH
        if "ssh" in payload.lower():
            ssh_patterns = [
                "failed password", "invalid password",
                "authentication failed", "permission denied",
                "failed login", "invalid login"
            ]
            if any(pattern in payload.lower() for pattern in ssh_patterns):
                threats.append(("SSH_BRUTEFORCE", 4))

        # Détection de Shellshock
        if "User-Agent" in headers or "Referer" in headers:
            shellshock_patterns = [
                "() {", ">{", "<{", "};",
                "*;", "@{", "${", "%(["
            ]
            headers_str = str(headers)
            if any(pattern in headers_str for pattern in shellshock_patterns):
                threats.append(("SHELLSHOCK", 5))

        return threats

    def analyze_ssh_activity(self, ip_address, username, command=None, success=False):
        """Analyse l'activité SSH pour détecter des comportements suspects"""
        threats = []
        
        # Liste de commandes suspectes
        suspicious_commands = [
            "wget", "curl", "nc", "netcat",
            "chmod 777", "rm -rf", "mkfifo",
            "python -c", "perl -e", "ruby -e",
            "base64 -d", "uname -a", "id",
            "cat /etc/passwd", "cat /etc/shadow",
            "ps aux", "netstat", "ss -tunlp",
            "iptables", "tcpdump", "dd if=",
            "socat", "nohup", "screen -d"
        ]

        # Vérifier les commandes suspectes
        if command:
            if any(cmd in command.lower() for cmd in suspicious_commands):
                threats.append(("SUSPICIOUS_SSH_COMMAND", 3))
            
            # Détection de téléchargement de malware
            if any(x in command.lower() for x in [".sh", ".pl", ".py", ".exe"]):
                if any(y in command.lower() for y in ["wget", "curl", "fetch", "lynx"]):
                    threats.append(("MALWARE_DOWNLOAD", 5))

        # Vérifier les noms d'utilisateur suspects
        suspicious_usernames = [
            "root", "admin", "administrator", "postgres",
            "mysql", "oracle", "guest", "test", "user",
            "default", "ubuntu", "centos", "ec2-user"
        ]
        if username.lower() in suspicious_usernames and not success:
            threats.append(("SUSPICIOUS_SSH_USERNAME", 2))

        return threats

    def analyze_network_activity(self, ip_address, port, protocol):
        """Analyse l'activité réseau pour détecter des comportements suspects"""
        threats = []
        
        # Ports communément utilisés pour les attaques
        suspicious_ports = {
            21: "FTP", 22: "SSH", 23: "TELNET",
            25: "SMTP", 445: "SMB", 1433: "MSSQL",
            3306: "MYSQL", 3389: "RDP", 5432: "POSTGRES",
            6379: "REDIS", 27017: "MONGODB"
        }

        if port in suspicious_ports:
            threats.append((f"{suspicious_ports[port]}_SCAN", 2))

        # Détecter les scans de ports séquentiels
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Vérifier les derniers ports scannés par cette IP
        c.execute("""SELECT port FROM port_scans 
                    WHERE ip_address = ? 
                    ORDER BY timestamp DESC LIMIT 10""",
                 (ip_address,))
        recent_ports = [row[0] for row in c.fetchall()]
        
        # Si plus de 5 ports différents en séquence, considérer comme scan
        if len(recent_ports) >= 5:
            threats.append(("PORT_SCANNING", 4))

        # Enregistrer le port scanné
        c.execute("INSERT INTO port_scans (ip_address, port, timestamp) VALUES (?, ?, ?)",
                  (ip_address, port, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return threats

    def check_ip_reputation(self, ip_address):
        """Vérifie la réputation d'une IP via une API externe"""
        try:
            # Exemple avec l'API AbuseIPDB (vous devrez vous inscrire pour obtenir une clé API)
            url = 'https://api.abuseipdb.com/api/v2/check'
            headers = {
                'Accept': 'application/json',
                'Key': '38721a2dce682a93d7abf4aaef1517750f667070102a0792cd59ea1d32cdb82d25ba57876053533e' # À configurer dans config.py
            }
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': 90
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['data']['abuseConfidenceScore'] > 80:
                    self.ban_ip(ip_address, "Bad IP reputation from AbuseIPDB")
                    return True
        except Exception as e:
            honeypot_logger.error(f"Error checking IP reputation: {str(e)}")
        return False

    def get_threat_stats(self):
        """Récupère les statistiques des menaces"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        stats = {
            'total_banned_ips': len(self.banned_ips),
            'recent_threats': [],
            'top_attack_types': {},
            'high_risk_ips': []
        }
        
        # Récupérer les menaces récentes
        c.execute("""SELECT ip_address, score, last_attack, attack_types 
                    FROM threat_scores 
                    ORDER BY last_attack DESC LIMIT 10""")
        for row in c.fetchall():
            stats['recent_threats'].append({
                'ip': row[0],
                'score': row[1],
                'last_attack': row[2],
                'attack_types': json.loads(row[3])
            })
        
        # Récupérer les IP à haut risque
        c.execute("""SELECT ip_address, score, attack_count 
                    FROM threat_scores 
                    WHERE score >= ? 
                    ORDER BY score DESC LIMIT 5""",
                 (BAN_THRESHOLD * 0.7,))
        stats['high_risk_ips'] = [
            {'ip': row[0], 'score': row[1], 'attacks': row[2]}
            for row in c.fetchall()
        ]
        
        conn.close()
        return stats

    def analyze_and_ban(self, log_entry):
        """
        Analyse comprehensive log entries and determine if an IP or user should be banned
        
        Args:
            log_entry (dict or str): Log entry containing attack information
        
        Returns:
            dict: Detailed ban information
        """
        try:
            # Ensure log_entry is a dictionary
            if isinstance(log_entry, str):
                try:
                    log_entry = json.loads(log_entry)
                except json.JSONDecodeError:
                    honeypot_logger.warning(f"Invalid log entry format: {log_entry}")
                    return None

            # Extract key information
            ip = log_entry.get('ip', 'unknown')
            attack_type = log_entry.get('type', 'UNKNOWN')
            timestamp = log_entry.get('timestamp', datetime.now().isoformat())
            
            # Predefined ban thresholds and criteria
            ban_criteria = {
                'PATH_TRAVERSAL': {
                    'threshold': 2,
                    'duration_hours': 24,
                    'severity': 5
                },
                'COMMAND_INJECTION': {
                    'threshold': 1,
                    'duration_hours': 48,
                    'severity': 7
                },
                'SQL_INJECTION': {
                    'threshold': 3,
                    'duration_hours': 72,
                    'severity': 6
                },
                'XSS': {
                    'threshold': 2,
                    'duration_hours': 36,
                    'severity': 5
                },
                'LOGIN_ATTEMPT': {
                    'threshold': 5,
                    'duration_hours': 12,
                    'severity': 3
                }
            }

            # Check if attack type is in ban criteria
            if attack_type not in ban_criteria:
                return None

            # Update threat score
            self.update_threat_score(ip, attack_type, ban_criteria[attack_type]['severity'])

            # Check threat score and ban if necessary
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            c.execute("""SELECT score, attack_count 
                         FROM threat_scores 
                         WHERE ip_address = ?""", (ip,))
            result = c.fetchone()
            
            if result:
                current_score, attack_count = result
                
                # Ban conditions
                if (current_score >= BAN_THRESHOLD or 
                    attack_count >= ban_criteria[attack_type]['threshold']):
                    
                    # Ban the IP
                    ban_info = {
                        'ip': ip,
                        'attack_type': attack_type,
                        'score': current_score,
                        'attack_count': attack_count,
                        'ban_duration': ban_criteria[attack_type]['duration_hours'],
                        'timestamp': timestamp
                    }
                    
                    # Actual banning
                    self.ban_ip(
                        ip, 
                        reason=f"Multiple {attack_type} attempts", 
                        duration_hours=ban_criteria[attack_type]['duration_hours']
                    )
                    
                    conn.close()
                    return ban_info

            conn.close()
            return None

        except Exception as e:
            honeypot_logger.error(f"Error in analyze_and_ban: {str(e)}")
            return None

    def process_log_entry(self, log_entry):
        """
        Enhanced log processing with automatic banning
        
        Args:
            log_entry (dict or str): Log entry to process
        
        Returns:
            list: List of detected threats
        """
        threats = []
        
        try:
            # Analyze the log entry
            ban_result = self.analyze_and_ban(log_entry)
            
            # If banned, add to threats
            if ban_result:
                threats.append((
                    f"BANNED_{ban_result['attack_type']}",
                    ban_result['score']
                ))
            
            # Existing threat detection logic
            if isinstance(log_entry, str):
                try:
                    log_data = json.loads(log_entry)
                except json.JSONDecodeError:
                    return threats

            # Additional threat detection methods
            ip_address = log_data.get('ip', '')
            
            if ip_address:
                # Check IP reputation
                if self.check_ip_reputation(ip_address):
                    threats.append(("BAD_REPUTATION_IP", 4))
                
                # Analyze network activity if port information exists
                if 'port' in log_data:
                    network_threats = self.analyze_network_activity(
                        ip_address, 
                        log_data.get('port', 0), 
                        log_data.get('protocol', 'tcp')
                    )
                    threats.extend(network_threats)

        except Exception as e:
            honeypot_logger.error(f"Error processing log entry: {str(e)}")
        
        return threats

    def get_banned_ips(self):
        """
        Retrieve all currently banned IPs with their ban details
        
        Returns:
            list: List of banned IP details
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("""SELECT ip_address, ban_timestamp, reason, expires 
                     FROM banned_ips 
                     WHERE expires > ?""", 
                  (datetime.now().isoformat(),))
        
        banned_ips = [
            {
                'ip': row[0],
                'banned_at': row[1],
                'reason': row[2],
                'expires': row[3]
            } for row in c.fetchall()
        ]
        
        conn.close()
        return banned_ips

    def process_log_file(self, log_file_path):
        """Traite un fichier de log complet"""
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    threats = self.process_log_entry(line.strip())
                    if threats:
                        honeypot_logger.warning(
                            f"Menaces détectées dans le log: {threats}"
                        )
        except Exception as e:
            honeypot_logger.error(f"Erreur lors du traitement du fichier log: {str(e)}")

    def monitor_log_file(self, log_file_path):
        """Surveille un fichier log en temps réel"""
        import time
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                # Aller à la fin du fichier
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        threats = self.process_log_entry(line.strip())
                        if threats:
                            honeypot_logger.warning(
                                f"Menaces détectées en temps réel: {threats}"
                            )
                    else:
                        time.sleep(0.1)  # Attendre de nouvelles entrées
        except Exception as e:
            honeypot_logger.error(f"Erreur lors de la surveillance du log: {str(e)}")
