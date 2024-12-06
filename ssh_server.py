import paramiko
import socket
import threading
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ssh/honeypot.log'),
        logging.StreamHandler()
    ]
)

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip, client_port):
        self.event = threading.Event()
        self.shell = FakeShell()
        self.client_ip = client_ip
        self.client_port = client_port
        self.session_id = None

    def check_auth_password(self, username, password):
        # Log tentative de connexion
        success = (username == "root" and password == "123456") or \
                 (username == "admin" and password == "admin123") or \
                 (username == "ubuntu" and password == "ubuntu")
        
        ssh_logger.log_login_attempt(self.client_ip, username, password, success)
        
        if success:
            self.shell.username = username
            self.session_id = ssh_logger.log_session_start(self.client_ip, self.client_port, username)
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

class HoneypotSSHServer:
    def __init__(self, host='0.0.0.0', port=22):
        self.host = host
        self.port = port
        self.ssh_logs_dir = '/var/log/ssh'
        os.makedirs(self.ssh_logs_dir, exist_ok=True)

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        logging.info(f"SSH Honeypot listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client, 
                args=(client_socket, addr)
            )
            client_thread.start()

    def handle_client(self, client_socket, addr):
        client_ip, client_port = addr
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip_address': client_ip,
            'port': client_port,
            'status': 'connection_attempt'
        }

        try:
            # Simulate SSH interaction
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(paramiko.RSAKey.generate(2048))
            
            server = SSHServer(addr[0], addr[1])
            transport.start_server(server=server)

            # Log connection details
            self.log_ssh_attempt(log_entry)

            channel = transport.accept(20)
            if not channel:
                transport.close()
                return
            
            server.event.wait(10)
            if not server.event.is_set():
                transport.close()
                return

            shell = server.shell
            channel.send(f"Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-42-generic x86_64)\n\n")
            
            while True:
                channel.send(shell.get_prompt())
                command = ""
                
                while True:
                    char = channel.recv(1).decode('utf-8')
                    if char == '\r':
                        channel.send('\n')
                        break
                    elif char == '\x03':  # Ctrl+C
                        channel.send('^C\n')
                        command = ''
                        break
                    elif char == '\x7f':  # Backspace
                        if command:
                            command = command[:-1]
                            channel.send('\b \b')
                    else:
                        command += char
                        channel.send(char)

                if command.strip().lower() in ['exit', 'logout']:
                    channel.send('logout\n')
                    break

                # Exécuter la commande et logger
                output = shell.execute(command)
                ssh_logger.log_command(
                    server.session_id,
                    shell.username,
                    command,
                    output,
                    shell.fs.current_path,
                    shell.is_root
                )
                
                if output:
                    channel.send(output + '\n')

        except Exception as e:
            log_entry['status'] = 'error'
            log_entry['error'] = str(e)
            logging.error(f"SSH Connection Error: {e}")
        finally:
            # Log fin de session
            if hasattr(server, 'session_id') and server.session_id:
                duration = time.time() - start_time
                ssh_logger.log_session_end(server.session_id, duration)
            try:
                transport.close()
            except:
                pass

    def log_ssh_attempt(self, log_entry):
        log_file = os.path.join(
            self.ssh_logs_dir, 
            f"ssh_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)

def main():
    honeypot = HoneypotSSHServer()
    honeypot.start_server()

if __name__ == '__main__':
    main()
