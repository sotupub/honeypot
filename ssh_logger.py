import os
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

class SSHLogger:
    def __init__(self):
        # Créer le dossier logs s'il n'existe pas
        self.logs_dir = "logs"
        self.ssh_logs_dir = os.path.join(self.logs_dir, "ssh")
        os.makedirs(self.ssh_logs_dir, exist_ok=True)

        # Logger pour les sessions SSH
        self.session_logger = logging.getLogger('ssh_sessions')
        self.session_logger.setLevel(logging.INFO)
        
        session_handler = RotatingFileHandler(
            os.path.join(self.ssh_logs_dir, 'ssh_sessions.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        session_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.session_logger.addHandler(session_handler)

        # Logger pour les commandes
        self.command_logger = logging.getLogger('ssh_commands')
        self.command_logger.setLevel(logging.INFO)
        
        command_handler = RotatingFileHandler(
            os.path.join(self.ssh_logs_dir, 'ssh_commands.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        command_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.command_logger.addHandler(command_handler)

    def log_session_start(self, ip, port, username):
        """Log le début d'une session SSH"""
        session_id = f"{ip}_{port}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            "session_id": session_id,
            "ip": ip,
            "port": port,
            "username": username,
            "start_time": datetime.now().isoformat(),
            "status": "started"
        }
        
        self.session_logger.info(f"New SSH session: {json.dumps(session_data)}")
        return session_id

    def log_session_end(self, session_id, duration):
        """Log la fin d'une session SSH"""
        session_data = {
            "session_id": session_id,
            "end_time": datetime.now().isoformat(),
            "duration": duration,
            "status": "ended"
        }
        
        self.session_logger.info(f"SSH session ended: {json.dumps(session_data)}")

    def log_command(self, session_id, username, command, output, working_dir, is_root=False):
        """Log une commande exécutée pendant une session SSH"""
        command_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "is_root": is_root,
            "working_dir": working_dir,
            "command": command,
            "output": output
        }
        
        self.command_logger.info(f"Command executed: {json.dumps(command_data)}")

    def log_login_attempt(self, ip, username, password, success):
        """Log une tentative de connexion SSH"""
        attempt_data = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "username": username,
            "password": password,
            "success": success
        }
        
        self.session_logger.warning(f"Login attempt: {json.dumps(attempt_data)}")

    def get_session_logs(self, session_id=None):
        """Récupère les logs d'une session spécifique ou de toutes les sessions"""
        logs = []
        try:
            with open(os.path.join(self.ssh_logs_dir, 'ssh_sessions.log'), 'r') as f:
                for line in f:
                    if session_id:
                        if session_id in line:
                            logs.append(line.strip())
                    else:
                        logs.append(line.strip())
        except FileNotFoundError:
            pass
        return logs

    def get_command_logs(self, session_id=None):
        """Récupère les logs des commandes d'une session spécifique ou de toutes les sessions"""
        logs = []
        try:
            with open(os.path.join(self.ssh_logs_dir, 'ssh_commands.log'), 'r') as f:
                for line in f:
                    if session_id:
                        if session_id in line:
                            logs.append(line.strip())
                    else:
                        logs.append(line.strip())
        except FileNotFoundError:
            pass
        return logs

# Instance globale du logger SSH
ssh_logger = SSHLogger()
