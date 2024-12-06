import os
import json
import random
import time
from datetime import datetime
from logger import honeypot_logger

class FakeFileSystem:
    def __init__(self):
        # Structure du système de fichiers simulé
        self.filesystem = {
            '/': {
                'type': 'dir',
                'content': {
                    'home': {
                        'type': 'dir',
                        'content': {
                            'ubuntu': {
                                'type': 'dir',
                                'content': {
                                    '.ssh': {
                                        'type': 'dir',
                                        'content': {
                                            'authorized_keys': {
                                                'type': 'file',
                                                'content': ''
                                            }
                                        }
                                    },
                                    'documents': {
                                        'type': 'dir',
                                        'content': {
                                            'passwords.txt': {
                                                'type': 'file',
                                                'content': 'admin:supersecret\nroot:toor123\n'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'etc': {
                        'type': 'dir',
                        'content': {
                            'passwd': {
                                'type': 'file',
                                'content': 'root:x:0:0:root:/root:/bin/bash\nubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n'
                            },
                            'shadow': {
                                'type': 'file',
                                'content': 'root:$6$xyz.../:18000:0:99999:7:::\nubuntu:$6$abc.../:18000:0:99999:7:::\n'
                            }
                        }
                    },
                    'var': {
                        'type': 'dir',
                        'content': {
                            'log': {
                                'type': 'dir',
                                'content': {}
                            }
                        }
                    }
                }
            }
        }
        self.current_path = '/home/ubuntu'

    def get_absolute_path(self, path):
        if path.startswith('/'):
            return path
        return os.path.normpath(os.path.join(self.current_path, path))

    def get_node(self, path):
        if path == '/':
            return self.filesystem['/']
        
        parts = path.strip('/').split('/')
        current = self.filesystem['/']
        
        for part in parts:
            if part == '':
                continue
            if part == '.':
                continue
            if part == '..':
                parts = path.strip('/').split('/')
                parts.pop()
                continue
            if 'content' in current and part in current['content']:
                current = current['content'][part]
            else:
                return None
        return current

class FakeShell:
    def __init__(self):
        self.fs = FakeFileSystem()
        self.hostname = "ubuntu-server"
        self.username = "ubuntu"
        self.is_root = False
        self.command_history = []
        
        # Commandes simulées et leurs réponses
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'cat': self.cmd_cat,
            'whoami': self.cmd_whoami,
            'id': self.cmd_id,
            'uname': self.cmd_uname,
            'ps': self.cmd_ps,
            'netstat': self.cmd_netstat,
            'wget': self.cmd_wget,
            'curl': self.cmd_curl,
            'sudo': self.cmd_sudo
        }

    def log_command(self, command, output):
        """Log la commande exécutée"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'username': self.username,
            'is_root': self.is_root,
            'command': command,
            'output': output,
            'working_dir': self.fs.current_path
        }
        honeypot_logger.warning(f"Command executed: {json.dumps(log_entry)}")
        self.command_history.append(log_entry)

    def get_prompt(self):
        """Retourne le prompt du shell"""
        if self.is_root:
            return f"root@{self.hostname}:{self.fs.current_path}# "
        return f"{self.username}@{self.hostname}:{self.fs.current_path}$ "

    def execute(self, command):
        """Exécute une commande et retourne la sortie"""
        if not command.strip():
            return ""

        # Diviser la commande et ses arguments
        parts = command.strip().split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Simuler un petit délai pour plus de réalisme
        time.sleep(random.uniform(0.1, 0.3))

        # Exécuter la commande si elle existe
        if cmd in self.commands:
            output = self.commands[cmd](args)
        else:
            output = f"bash: {cmd}: command not found"

        # Logger la commande
        self.log_command(command, output)
        return output

    def cmd_ls(self, args):
        """Simule la commande ls"""
        path = args[0] if args else '.'
        abs_path = self.fs.get_absolute_path(path)
        node = self.fs.get_node(abs_path)
        
        if not node or node['type'] != 'dir':
            return f"ls: cannot access '{path}': No such file or directory"
            
        files = []
        for name, item in node['content'].items():
            if item['type'] == 'dir':
                files.append(f"\033[1;34m{name}/\033[0m")
            else:
                files.append(name)
        return "  ".join(files)

    def cmd_cd(self, args):
        """Simule la commande cd"""
        path = args[0] if args else '/home/' + self.username
        new_path = self.fs.get_absolute_path(path)
        node = self.fs.get_node(new_path)
        
        if not node or node['type'] != 'dir':
            return f"cd: {path}: No such file or directory"
            
        self.fs.current_path = new_path
        return ""

    def cmd_pwd(self, args):
        """Simule la commande pwd"""
        return self.fs.current_path

    def cmd_cat(self, args):
        """Simule la commande cat"""
        if not args:
            return "usage: cat [file]"
            
        path = args[0]
        abs_path = self.fs.get_absolute_path(path)
        node = self.fs.get_node(abs_path)
        
        if not node or node['type'] != 'file':
            return f"cat: {path}: No such file or directory"
            
        return node['content']

    def cmd_whoami(self, args):
        """Simule la commande whoami"""
        return 'root' if self.is_root else self.username

    def cmd_id(self, args):
        """Simule la commande id"""
        if self.is_root:
            return "uid=0(root) gid=0(root) groups=0(root)"
        return f"uid=1000({self.username}) gid=1000({self.username}) groups=1000({self.username}),4(adm),24(cdrom),27(sudo)"

    def cmd_uname(self, args):
        """Simule la commande uname"""
        if '-a' in args:
            return "Linux ubuntu-server 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"
        return "Linux"

    def cmd_ps(self, args):
        """Simule la commande ps"""
        processes = """  PID TTY          TIME CMD
    1 ?        00:00:01 systemd
  423 ?        00:00:00 sshd
  892 ?        00:00:00 nginx
 1234 pts/0    00:00:00 bash
 1337 pts/0    00:00:00 ps"""
        return processes

    def cmd_netstat(self, args):
        """Simule la commande netstat"""
        connections = """Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN     
tcp        0    304 192.168.1.100:22        192.168.1.10:59834     ESTABLISHED"""
        return connections

    def cmd_wget(self, args):
        """Simule la commande wget"""
        if not args:
            return "wget: missing URL"
        url = args[0]
        return f"""--2023-12-05 20:45:01--  {url}
Resolving {url.split('/')[2]}... 93.184.216.34
Connecting to {url.split('/')[2]}... connected.
HTTP request sent, awaiting response... 404 Not Found
2023-12-05 20:45:02 ERROR 404: Not Found."""

    def cmd_curl(self, args):
        """Simule la commande curl"""
        if not args:
            return "curl: try 'curl --help' or 'curl --manual' for more information"
        url = args[-1]
        return f"""curl: (7) Failed to connect to {url.split('/')[2]} port 80: Connection refused"""

    def cmd_sudo(self, args):
        """Simule la commande sudo"""
        if not args:
            return "usage: sudo command"
            
        if self.is_root:
            return self.execute(' '.join(args))
            
        if random.random() < 0.3:  # 30% de chance de devenir root
            self.is_root = True
            return self.execute(' '.join(args))
        return "sudo: 3 incorrect password attempts"
