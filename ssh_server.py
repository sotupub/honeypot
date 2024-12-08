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

logger = logging.getLogger('honeypot')

class SSHLogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
    def log_login_attempt(self, ip, username, password, success):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'username': username,
            'password': password,
            'success': success,
            'type': 'login_attempt'
        }
        logger.info(f"Login attempt from {ip} - Username: {username} - Success: {success}")
        self._write_log(log_entry)
        
    def log_session_start(self, ip, port, username):
        session_id = f"{ip}-{port}-{int(datetime.now().timestamp())}"
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'port': port,
            'username': username,
            'session_id': session_id,
            'type': 'session_start'
        }
        logger.info(f"Session started - ID: {session_id} - IP: {ip} - Username: {username}")
        self._write_log(log_entry)
        return session_id
        
    def log_session_end(self, session_id, duration):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'duration': duration,
            'type': 'session_end'
        }
        logger.info(f"Session ended - ID: {session_id} - Duration: {duration} seconds")
        self._write_log(log_entry)
        
    def log_command(self, session_id, username, command, output, cwd, is_root):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'username': username,
            'command': command,
            'output': output,
            'cwd': cwd,
            'is_root': is_root,
            'type': 'command'
        }
        logger.info(f"Command executed - ID: {session_id} - Username: {username} - Command: {command}")
        self._write_log(log_entry)
        
    def _write_log(self, log_entry):
        log_file = os.path.join(self.log_dir, 'access.log')
        with open(log_file, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')

class FakeShell:
    def __init__(self):
        self.username = None
        self.cwd = "/home/user"
        self.commands = {
            'ls': self._ls,
            'pwd': self._pwd,
            'cd': self._cd,
            'whoami': self._whoami,
            'id': self._id,
            'uname': self._uname,
            'echo': self._echo
        }
        
    def get_prompt(self):
        return f"{self.username}@ubuntu:{self.cwd}$ "
        
    def execute(self, cmd):
        if not cmd.strip():
            return ""
            
        parts = cmd.strip().split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            return self.commands[command](args)
        else:
            return f"bash: {command}: command not found"
            
    def _ls(self, args):
        return "Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos"
        
    def _pwd(self, args):
        return self.cwd
        
    def _cd(self, args):
        if not args:
            self.cwd = "/home/user"
        elif args[0] == "..":
            if self.cwd != "/":
                self.cwd = "/".join(self.cwd.split("/")[:-1]) or "/"
        else:
            # Simulate changing directory
            self.cwd = args[0] if args[0].startswith("/") else f"{self.cwd}/{args[0]}"
        return ""
        
    def _whoami(self, args):
        return self.username
        
    def _id(self, args):
        return f"uid=1000({self.username}) gid=1000({self.username}) groups=1000({self.username}),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lpadmin),132(lxd),133(sambashare)"
        
    def _uname(self, args):
        if "-a" in args:
            return "Linux ubuntu 5.15.0-89-generic #99-Ubuntu SMP Mon Oct 30 20:42:41 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux"
        return "Linux"
        
    def _echo(self, args):
        return " ".join(args)

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip, client_port):
        self.event = threading.Event()
        self.shell = FakeShell()
        self.client_ip = client_ip
        self.client_port = client_port
        self.session_id = None
        self.ssh_logger = SSHLogger('/var/log/ssh')
        self.start_time = None

    def check_auth_password(self, username, password):
        success = (username == "root" and password == "123456") or \
                 (username == "ubuntu" and password == "ubuntu123")
        
        # Log login attempt
        self.ssh_logger.log_login_attempt(self.client_ip, username, password, success)
        
        if success:
            self.shell.username = username
            self.session_id = self.ssh_logger.log_session_start(self.client_ip, self.client_port, username)
            self.start_time = datetime.now()
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        if self.session_id:
            output = self.shell.execute(command.decode())
            self.ssh_logger.log_command(
                self.session_id,
                self.shell.username,
                command.decode(),
                output,
                self.shell.cwd,
                self.shell.username == "root"
            )
        return True

class HoneypotSSHServer:
    def __init__(self, host='0.0.0.0', port=22222):
        self.host = host
        self.port = port
        self.ssh_logs_dir = '/var/log/ssh'
        os.makedirs(self.ssh_logs_dir, exist_ok=True)
        self.ssh_logger = SSHLogger(self.ssh_logs_dir)

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
        transport = None
        channel = None
        server = None
        try:
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(paramiko.RSAKey.generate(2048))
            
            server = SSHServer(addr[0], addr[1])
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                logger.error('SSH negotiation failed.')
                return

            channel = transport.accept(20)
            if channel is None:
                logger.error('No channel.')
                return

            server.event.wait(10)
            if not server.event.is_set():
                logger.error('Client never asked for a shell')
                return

            # Send welcome message
            welcome_msg = "Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-42-generic x86_64)\n\n"
            channel.send(welcome_msg.encode('utf-8'))
            channel.send(server.shell.get_prompt().encode('utf-8'))

            # Interactive shell session
            while True:
                if not channel.recv_ready():
                    if channel.exit_status_ready():
                        break
                    continue

                try:
                    command = channel.recv(1024).decode('utf-8').strip()
                    if not command:
                        continue

                    if command.lower() in ['exit', 'logout']:
                        channel.send('logout\n'.encode('utf-8'))
                        break

                    output = server.shell.execute(command)
                    server.ssh_logger.log_command(
                        server.session_id,
                        server.shell.username,
                        command,
                        output,
                        server.shell.cwd,
                        server.shell.username == "root"
                    )

                    response = f"{output}\n{server.shell.get_prompt()}"
                    channel.send(response.encode('utf-8'))
                except UnicodeDecodeError:
                    logger.error("Failed to decode command")
                    continue
                except Exception as e:
                    logger.error(f"Error processing command: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"SSH Connection Error: {str(e)}")
        finally:
            try:
                if server and hasattr(server, 'session_id') and server.session_id and hasattr(server, 'start_time'):
                    duration = (datetime.now() - server.start_time).total_seconds()
                    server.ssh_logger.log_session_end(server.session_id, duration)
            except Exception as e:
                logger.error(f"Error logging session end: {str(e)}")
            
            try:
                if channel:
                    channel.close()
            except Exception as e:
                logger.error(f"Error closing channel: {str(e)}")
                
            try:
                if transport:
                    transport.close()
            except Exception as e:
                logger.error(f"Error closing transport: {str(e)}")
                
            try:
                client_socket.close()
            except Exception as e:
                logger.error(f"Error closing client socket: {str(e)}")

def main():
    honeypot = HoneypotSSHServer()
    honeypot.start_server()

if __name__ == '__main__':
    main()
