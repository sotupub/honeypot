import socket
import threading
import sqlite3
import datetime
from config import *
from logger import honeypot_logger, log_attack
import json
from services import start_services
from threat_manager import ThreatManager

class HoneypotServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.setup_database()
        self.threat_manager = ThreatManager()
        honeypot_logger.info("Honeypot server initialized")

    def setup_database(self):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attacks
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp TEXT,
                     ip_address TEXT,
                     attack_type TEXT,
                     username TEXT,
                     password TEXT,
                     payload TEXT,
                     headers TEXT,
                     additional_info TEXT)''')
        conn.commit()
        conn.close()
        honeypot_logger.info("Database initialized")

    def log_attack(self, ip_address, username, password, attack_type="SSH", payload="", headers="", additional_info=""):
        # Vérifier si l'IP est déjà bannie
        if self.threat_manager.is_ip_banned(ip_address):
            honeypot_logger.info(f"Blocked attempt from banned IP: {ip_address}")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        # Log dans la base de données
        c.execute("""
            INSERT INTO attacks 
            (timestamp, ip_address, attack_type, username, password, payload, headers, additional_info) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, ip_address, attack_type, username, password, payload, headers, additional_info))
        conn.commit()
        conn.close()

        # Analyser la menace
        if payload:
            threats = self.threat_manager.analyze_payload(payload, headers)
            for threat_type, severity in threats:
                self.threat_manager.update_threat_score(ip_address, threat_type, severity)

        # Log dans les fichiers de log
        attack_details = {
            'timestamp': timestamp,
            'username': username,
            'password': password,
            'payload': payload,
            'headers': headers,
            'additional_info': additional_info
        }
        log_attack(ip_address, attack_type, json.dumps(attack_details))
        honeypot_logger.warning(f"Attack detected from {ip_address}")

    def handle_connection(self, client_socket, address):
        ip_address = address[0]
        honeypot_logger.info(f"New connection from {ip_address}")
        
        try:
            # Simuler une bannière SSH
            banner = "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\\r\\n"
            client_socket.send(banner.encode())
            honeypot_logger.debug(f"Sent SSH banner to {ip_address}")
            
            # Collecter toutes les données envoyées
            all_data = ""
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    all_data += data
                    
                    # Analyser les tentatives de connexion
                    if "login" in data.lower() or "user" in data.lower():
                        username = data.split()[-1]
                        client_socket.send(b"Password: ")
                        password_data = client_socket.recv(1024).decode('utf-8').strip()
                        
                        # Log l'attaque avec plus de détails
                        self.log_attack(
                            ip_address=ip_address,
                            username=username,
                            password=password_data,
                            payload=all_data,
                            headers=str(client_socket.getpeername()),
                            additional_info="SSH login attempt"
                        )
                        
                        # Simuler un échec d'authentification
                        client_socket.send(b"Access denied\\r\\n")
                        honeypot_logger.info(f"Failed login attempt from {ip_address} - User: {username}")
                        
                except socket.timeout:
                    break
                
        except Exception as e:
            honeypot_logger.error(f"Error with connection from {ip_address}: {str(e)}")
        finally:
            client_socket.close()
            honeypot_logger.info(f"Connection closed from {ip_address}")

    def start(self):
        try:
            # Démarrer le service SSH
            self.sock.bind((HONEYPOT_HOST, HONEYPOT_PORTS['ssh']))
            self.sock.listen(5)
            honeypot_logger.info(f"SSH Honeypot started on {HONEYPOT_HOST}:{HONEYPOT_PORTS['ssh']}")

            # Démarrer les autres services vulnérables
            services, service_threads = start_services()
            honeypot_logger.info("Started vulnerable services")

            while True:
                client, address = self.sock.accept()
                client.settimeout(10)  # Timeout de 10 secondes
                client_handler = threading.Thread(
                    target=self.handle_connection,
                    args=(client, address)
                )
                client_handler.start()
                self.connections.append(client_handler)

        except Exception as e:
            honeypot_logger.error(f"Server error: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        honeypot_logger.info("Stopping honeypot...")
        for conn in self.connections:
            if conn.is_alive():
                conn.join()
        self.sock.close()
        honeypot_logger.info("Honeypot stopped")

if __name__ == "__main__":
    server = HoneypotServer()
    server.start()
