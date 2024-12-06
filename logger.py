import logging
from logging.handlers import RotatingFileHandler
import os
from config import *

class LoggerSetup:
    @staticmethod
    def setup_logger(name, log_file, level=LOG_LEVEL, format=LOG_FORMAT):
        """Configure un logger avec rotation des fichiers"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Créer le dossier logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)
        log_path = os.path.join('logs', log_file)

        # Handler pour la rotation des fichiers
        handler = RotatingFileHandler(
            log_path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)

        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(format))
        logger.addHandler(console_handler)

        return logger

# Création des loggers spécifiques
honeypot_logger = LoggerSetup.setup_logger('honeypot', LOG_FILE)
access_logger = LoggerSetup.setup_logger('access', ACCESS_LOG_FILE)
api_logger = LoggerSetup.setup_logger('api', API_LOG_FILE, format=DETAILED_LOG_FORMAT)
attack_logger = LoggerSetup.setup_logger('attack', ATTACK_LOG_FILE, format=DETAILED_LOG_FORMAT)

def log_access(request, status_code):
    """Log les accès HTTP"""
    access_logger.info(
        f"IP: {request.remote_addr} - "
        f"Method: {request.method} - "
        f"Path: {request.path} - "
        f"Status: {status_code} - "
        f"User-Agent: {request.headers.get('User-Agent')}"
    )

def log_api_call(request, response):
    """Log les appels API"""
    api_logger.info(
        f"API Call - IP: {request.remote_addr} - "
        f"Method: {request.method} - "
        f"Path: {request.path} - "
        f"Status: {response.status_code} - "
        f"Request Data: {request.get_data(as_text=True)}"
    )

def log_attack(ip_address, attack_type, details):
    """Log les attaques détectées"""
    attack_logger.warning(
        f"Attack Detected - "
        f"IP: {ip_address} - "
        f"Type: {attack_type} - "
        f"Details: {details}"
    )
