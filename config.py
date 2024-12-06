import os
import logging

# Configuration du honeypot
HONEYPOT_HOST = '0.0.0.0'
HONEYPOT_PORTS = {
    'ssh': 2222,
    'ftp': 2121,
    'telnet': 2323,
    'http': 8080,
    'smtp': 2525
}

# Configuration de la base de données
DATABASE_FILE = 'honeypot.db'

# Configuration du logging
LOG_FILE = 'honeypot.log'
ACCESS_LOG_FILE = 'access.log'
API_LOG_FILE = 'api.log'
ATTACK_LOG_FILE = 'attacks.log'

# Niveaux de logging
LOG_LEVEL = logging.DEBUG

# Format des logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'

# Configuration de rotation des logs
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# Configuration de l'interface web
WEB_PORT = 5000
SECRET_KEY = os.urandom(24)

# Configuration de la gestion des menaces
BAN_THRESHOLD = 10  # Score à partir duquel une IP est bannie
BAN_DURATION = 24  # Durée du bannissement en heures
THREAT_SCORE_DECAY = 0.5  # Facteur de décroissance du score de menace par heure

# Simulation de vulnérabilités
VULNERABILITIES = {
    'sql_injection': True,
    'xss': True,
    'command_injection': True,
    'default_credentials': True,
    'directory_traversal': True
}

# Liste des services vulnérables à simuler
VULNERABLE_SERVICES = {
    'ftp': {
        'enabled': True,
        'port': 2121,
        'banner': 'vsFTPd 2.3.4'
    },
    'telnet': {
        'enabled': True,
        'port': 2323,
        'banner': 'Ubuntu 18.04 LTS'
    },
    'http': {
        'enabled': True,
        'port': 8080,
        'server': 'Apache/2.4.29'
    },
    'smtp': {
        'enabled': True,
        'port': 2525,
        'banner': 'Postfix SMTP'
    }
}

# SSH Configuration
SSH_PORT = 2222
SSH_KEY_FILE = "ssh_host_rsa"
SSH_BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2"

# Fake credentials pour le honeypot
FAKE_CREDENTIALS = [
    ("root", "123456"),
    ("admin", "admin123"),
    ("ubuntu", "ubuntu")
]

# Identifiants factices pour la simulation
# FAKE_CREDENTIALS = {
#     'admin': ['admin123', 'password123', 'admin2023'],
#     'root': ['toor', 'root123', 'password'],
#     'user': ['123456', 'user123', 'password123']
# }

# Configuration des API externes
ABUSEIPDB_API_KEY = ''  # À remplir avec votre clé API
VIRUSTOTAL_API_KEY = ''  # À remplir avec votre clé API

# Paramètres de détection
DETECTION_THRESHOLDS = {
    'failed_login_attempts': 5,
    'concurrent_connections': 10,
    'requests_per_minute': 60,
    'payload_size': 1024 * 1024  # 1MB
}

# Configuration des alertes
ALERT_SETTINGS = {
    'email_enabled': False,
    'email_recipient': '',
    'telegram_enabled': False,
    'telegram_bot_token': '',
    'telegram_chat_id': ''
}
