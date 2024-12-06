import socket
import threading
import ssl
from logger import honeypot_logger
from config import *
import time
import random
import re

class VulnerableService:
    def __init__(self, port, service_type):
        self.port = port
        self.service_type = service_type
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.connections = []
        
    def start(self):
        try:
            self.sock.bind((HONEYPOT_HOST, self.port))
            self.sock.listen(5)
            self.running = True
            honeypot_logger.info(f"Started {self.service_type} service on port {self.port}")
            
            while self.running:
                client, address = self.sock.accept()
                client_handler = threading.Thread(
                    target=self.handle_connection,
                    args=(client, address)
                )
                client_handler.start()
                self.connections.append(client_handler)
                
        except Exception as e:
            honeypot_logger.error(f"Error in {self.service_type} service: {str(e)}")
        finally:
            self.stop()
            
    def stop(self):
        self.running = False
        for conn in self.connections:
            if conn.is_alive():
                conn.join()
        self.sock.close()
        
    def handle_connection(self, client, address):
        raise NotImplementedError()

class FTPService(VulnerableService):
    def __init__(self, port=21):
        super().__init__(port, "FTP")
        self.banner = "220 FTP Server (vsftpd 2.3.4)\r\n"
        
    def handle_connection(self, client, address):
        try:
            client.send(self.banner.encode())
            while True:
                data = client.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                    
                if data.startswith('USER'):
                    client.send(b"331 Please specify the password.\r\n")
                elif data.startswith('PASS'):
                    # Simuler une vulnérabilité vsftpd backdoor
                    if ':)' in data:
                        honeypot_logger.warning(f"Detected vsftpd backdoor attempt from {address[0]}")
                        time.sleep(1)  # Simuler un délai
                    client.send(b"530 Login incorrect.\r\n")
                else:
                    client.send(b"500 Unknown command.\r\n")
                    
        except Exception as e:
            honeypot_logger.error(f"FTP Error with {address[0]}: {str(e)}")
        finally:
            client.close()

class SMTPService(VulnerableService):
    def __init__(self, port=25):
        super().__init__(port, "SMTP")
        self.banner = "220 mail.example.com ESMTP Postfix\r\n"
        
    def handle_connection(self, client, address):
        try:
            client.send(self.banner.encode())
            while True:
                data = client.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                    
                if data.startswith('HELO') or data.startswith('EHLO'):
                    client.send(b"250 mail.example.com\r\n")
                elif data.startswith('MAIL FROM'):
                    # Simuler une vulnérabilité d'injection de commandes
                    if '|' in data or ';' in data:
                        honeypot_logger.warning(f"Detected SMTP command injection attempt from {address[0]}")
                    client.send(b"250 Ok\r\n")
                elif data.startswith('RCPT TO'):
                    client.send(b"250 Ok\r\n")
                elif data == 'DATA':
                    client.send(b"354 End data with <CR><LF>.<CR><LF>\r\n")
                elif data == '.':
                    client.send(b"250 Ok: queued as 12345\r\n")
                else:
                    client.send(b"500 Unknown command\r\n")
                    
        except Exception as e:
            honeypot_logger.error(f"SMTP Error with {address[0]}: {str(e)}")
        finally:
            client.close()

class HTTPService(VulnerableService):
    def __init__(self, port=80):
        super().__init__(port, "HTTP")
        
    def handle_connection(self, client, address):
        try:
            request = client.recv(1024).decode('utf-8')
            
            # Simuler une vulnérabilité d'injection SQL dans les paramètres GET
            if "id=" in request:
                param = re.search(r'id=([^&\s]+)', request)
                if param and ("'" in param.group(1) or '"' in param.group(1)):
                    honeypot_logger.warning(f"Detected SQL injection attempt from {address[0]}")
            
            # Simuler une vulnérabilité XSS
            if "<script>" in request or "javascript:" in request:
                honeypot_logger.warning(f"Detected XSS attempt from {address[0]}")
            
            # Réponse par défaut
            response = "HTTP/1.1 200 OK\r\n"
            response += "Server: Apache/2.4.29 (Ubuntu)\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += "<html><body><h1>Welcome to Example.com</h1></body></html>"
            
            client.send(response.encode())
            
        except Exception as e:
            honeypot_logger.error(f"HTTP Error with {address[0]}: {str(e)}")
        finally:
            client.close()

class TelnetService(VulnerableService):
    def __init__(self, port=23):
        super().__init__(port, "Telnet")
        self.banner = "\r\nWelcome to Ubuntu 18.04 LTS\r\n\r\nlogin: "
        
    def handle_connection(self, client, address):
        try:
            client.send(self.banner.encode())
            username = client.recv(1024).decode('utf-8').strip()
            client.send(b"Password: ")
            password = client.recv(1024).decode('utf-8').strip()
            
            # Simuler des identifiants par défaut
            if username in ['admin', 'root'] and password in ['admin', 'password', '123456']:
                honeypot_logger.warning(f"Default credential attempt from {address[0]}: {username}:{password}")
            
            # Simuler un délai et une erreur
            time.sleep(random.uniform(0.1, 0.5))
            client.send(b"\r\nLogin incorrect\r\n")
            client.send(self.banner.encode())
            
        except Exception as e:
            honeypot_logger.error(f"Telnet Error with {address[0]}: {str(e)}")
        finally:
            client.close()

def start_services():
    """Démarre tous les services vulnérables"""
    services = [
        FTPService(),
        SMTPService(),
        HTTPService(),
        TelnetService()
    ]
    
    threads = []
    for service in services:
        thread = threading.Thread(target=service.start)
        thread.start()
        threads.append(thread)
        
    return services, threads
