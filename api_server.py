from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os
from log_parser import LogParser
from ssh_log_parser import SSHLogParser
from threat_manager import ThreatManager  # Import the ThreatManager class

app = Flask(__name__)
CORS(app)

# Initialize log parsers
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
log_parser = LogParser(LOG_DIR)
ssh_parser = SSHLogParser(LOG_DIR)
threat_manager = ThreatManager()  # Initialize the ThreatManager instance

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        # Get attack statistics from log parser
        attack_stats = log_parser.get_attack_stats()
        
        # Get SSH statistics
        ssh_stats = ssh_parser.get_ssh_stats()
        
        # Format response
        response = {
            'stats': {
                'total_attacks': attack_stats['total_attacks'],
                'active_sessions': ssh_stats['active_sessions'],
                'blocked_ips': len([x for x in attack_stats.get('top_attackers', []) if x[1] > 10]),
                'unique_attackers': len(attack_stats.get('top_attackers', {}))
            },
            'recent_attacks': [
                {
                    'timestamp': attack[0],
                    'ip_address': attack[1],
                    'attack_type': attack[2],
                    'status': 'blocked' if any(ip[0] == attack[1] and ip[1] > 10 for ip in attack_stats.get('top_attackers', [])) else 'detected'
                }
                for attack in attack_stats.get('recent_attacks', [])
            ],
            'ssh_logs': ssh_stats['recent_commands']
        }
        
        print("\nDashboard Response:")
        print(json.dumps(response, indent=2))
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({
            'error': str(e),
            'stats': {
                'total_attacks': 0,
                'active_sessions': 0,
                'blocked_ips': 0,
                'unique_attackers': 0
            },
            'recent_attacks': [],
            'ssh_logs': []
        }), 500

@app.route('/api/ids/stats', methods=['GET'])
def get_ids_stats():
    try:
        # Get statistics from log parser
        stats = log_parser.get_attack_stats()
        
        response = {
            'total_attacks': stats['total_attacks'],
            'attack_types': stats['attack_types'],
            'top_attackers': stats['top_attackers'],
            'recent_attacks': stats['recent_attacks']
        }
        
        print("\nIDS Stats Response:")
        print(json.dumps(response, indent=2))
        
        return jsonify(response)
        
    except Exception as e:
        print(f"IDS stats error: {e}")
        return jsonify({
            'error': str(e),
            'total_attacks': 0,
            'attack_types': {},
            'top_attackers': [],
            'recent_attacks': []
        }), 500

@app.route('/api/analysis/full', methods=['GET'])
def get_full_analysis():
    try:
        # Get statistics from log parser
        stats = log_parser.get_attack_stats()
        
        # Format response
        response = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_attacks': stats['total_attacks'],
                'unique_ips': len(stats.get('top_attackers', {})),
                'blocked_ips': len([x for x in stats.get('top_attackers', []) if x[1] > 10]),  # IPs with more than 10 attempts
                'anomalies_detected': 0  # Not implemented
            },
            'patterns': {
                'temporal': {
                    'peak_hours': {},  # Not implemented
                    'busiest_days': {}  # Not implemented
                },
                'attack_types': {
                    'distribution': stats['attack_types'],
                    'success_rate': 0  # Not implemented
                },
                'geographic': None,  # Not implemented
                'anomalies': {
                    'count': 0,  # Not implemented
                    'percentage': 0  # Not implemented
                },
                'clusters': {
                    'count': 0,  # Not implemented
                    'distribution': {}  # Not implemented
                }
            },
            'high_risk_ips': [x[0] for x in stats.get('top_attackers', []) if x[1] > 10]  # IPs with more than 10 attempts
        }
        
        print("\nAPI Response Data Structure:")
        print("Keys in response:", list(response.keys()))
        print("\nSummary structure:", response.get('summary'))
        print("\nPatterns structure:", json.dumps(response.get('patterns', {}), indent=2))
        print("\nHigh risk IPs structure:", json.dumps(response.get('high_risk_ips', []), indent=2))
        
        return jsonify(response)
        
    except Exception as e:
        error_response = {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'summary': {'total_attacks': 0, 'unique_ips': 0, 'blocked_ips': 0, 'anomalies_detected': 0},
            'patterns': {
                'temporal': {'peak_hours': {}, 'busiest_days': {}},
                'attack_types': {'distribution': {}, 'success_rate': 0},
                'geographic': None,
                'anomalies': {'count': 0, 'percentage': 0},
                'clusters': {'count': 0, 'distribution': {}}
            },
            'high_risk_ips': []
        }
        print("\nAPI Error Response:")
        print(json.dumps(error_response, indent=2))
        return jsonify(error_response), 500

@app.route('/api/analysis/realtime/<ip>', methods=['GET'])
def get_realtime_analysis(ip):
    try:
        # Get statistics from log parser
        stats = log_parser.get_attack_stats()
        
        # Format response
        response = {
            'ip_address': ip,
            'is_blocked': any(ip == x[0] and x[1] > 10 for x in stats.get('top_attackers', [])),  # IPs with more than 10 attempts
            'block_reason': 'Suspicious activity',  # Not implemented
            'recent_activity': [x for x in stats.get('recent_attacks', []) if x[1] == ip]
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # Get statistics from log parser
        stats = log_parser.get_attack_stats()
        
        # Format response
        response = {
            'total_attacks': stats['total_attacks'],
            'attacks_by_type': stats['attack_types'],
            'top_attackers': stats['top_attackers'],
            'ssh_stats': {
                'total_sessions': 0,  # Not implemented
                'total_commands': 0,  # Not implemented
                'unique_ips': len(stats.get('top_attackers', {})),
                'recent_commands': []  # Not implemented
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attacks', methods=['GET'])
def get_attacks():
    try:
        # Get statistics from log parser
        stats = log_parser.get_attack_stats()
        
        # Format response
        response = {
            'attacks': stats['recent_attacks'],
            'total': stats['total_attacks'],
            'page': 1,
            'per_page': 10
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ssh/sessions', methods=['GET'])
def get_ssh_sessions():
    try:
        sessions = ssh_parser.get_ssh_sessions()
        return jsonify(sessions)
    except Exception as e:
        print(f"Error getting SSH sessions: {e}")
        return jsonify([]), 500

@app.route('/api/ssh/commands', methods=['GET'])
def get_ssh_commands():
    try:
        commands = ssh_parser.get_ssh_commands()
        return jsonify(commands)
    except Exception as e:
        print(f"Error getting SSH commands: {e}")
        return jsonify([]), 500

@app.route('/api/ssh/stats', methods=['GET'])
def get_ssh_stats():
    try:
        stats = ssh_parser.get_ssh_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting SSH stats: {e}")
        return jsonify({
            'total_sessions': 0,
            'active_sessions': 0,
            'total_commands': 0,
            'unique_users': 0,
            'unique_ips': 0,
            'command_types': {},
            'recent_commands': [],
            'recent_sessions': []
        }), 500

@app.route('/api/threats', methods=['GET'])
def get_threat_data():
    try:
        threat_stats = threat_manager.get_threat_stats()
        
        # Enrichir les données avec des informations supplémentaires
        threat_data = {
            'stats': threat_stats,
            'recent_threats': threat_stats['recent_threats'],
            'threat_categories': {
                'ssh_threats': {
                    'title': 'SSH Activity Detection',
                    'items': [
                        {'name': 'Username Tracking', 'status': True},
                        {'name': 'Command Monitoring', 'status': True},
                        {'name': 'Success/Failure Detection', 'status': True}
                    ]
                },
                'network_threats': {
                    'title': 'Network Security',
                    'items': [
                        {'name': 'Port Access Monitoring', 'status': True},
                        {'name': 'IP Reputation Checking', 'status': True},
                        {'name': 'Web Attack Detection', 'status': True}
                    ]
                },
                'system_features': {
                    'title': 'System Features',
                    'items': [
                        {'name': 'Real-time Updates', 'status': True},
                        {'name': 'Error Handling', 'status': True},
                        {'name': 'Threat Logging', 'status': True}
                    ]
                }
            }
        }
        return jsonify(threat_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/banned-ips', methods=['GET'])
def get_banned_ips():
    """
    Retrieve list of currently banned IPs
    """
    try:
        banned_ips = threat_manager.get_banned_ips()
        return jsonify({
            'banned_ips': banned_ips,
            'total_banned': len(banned_ips)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attacks/analyze', methods=['POST'])
def analyze_attack():
    try:
        data = request.get_json()
        
        if not data or 'ip_address' not in data or 'attack_type' not in data:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Analyze the attack with IDS
        analysis_result = log_parser.analyze_attack(data['ip_address'], data['attack_type'])
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file', methods=['GET'])
def get_file():
    """Endpoint pour simuler l'accès aux fichiers (honeypot)"""
    try:
        path = request.args.get('path', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Log l'tentative d'accès
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'path': path,
            'type': 'PATH_TRAVERSAL',
            'user_agent': user_agent
        }
        
        # Analyser la menace
        threat_manager.process_log_entry(json.dumps(log_entry))
        
        # Simuler une réponse d'erreur réaliste
        if '../' in path or '..' in path:
            return jsonify({'error': 'Access denied'}), 403
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Endpoint pour simuler l'exécution de commandes (honeypot)"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Log la tentative d'exécution
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'command': command,
            'type': 'COMMAND_INJECTION',
            'user_agent': user_agent
        }
        
        # Analyser la menace
        threat_manager.process_log_entry(json.dumps(log_entry))
        
        # Simuler une réponse d'erreur réaliste
        return jsonify({'error': 'Command execution failed: Permission denied'}), 403
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint pour simuler la connexion (honeypot)"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Log la tentative de connexion
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'username': username,
            'type': 'SQL_INJECTION' if any(x in username or x in password 
                for x in ["'", '"', ';', '--', '=', 'OR', 'AND']) else 'LOGIN_ATTEMPT',
            'user_agent': user_agent
        }
        
        # Analyser la menace
        threat_manager.process_log_entry(json.dumps(log_entry))
        
        # Simuler une réponse d'erreur réaliste
        return jsonify({'error': 'Invalid username or password'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comment', methods=['POST'])
def add_comment():
    """Endpoint pour simuler l'ajout de commentaires (honeypot)"""
    try:
        data = request.get_json()
        comment = data.get('comment', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Log la tentative
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'comment': comment,
            'type': 'XSS' if any(x in comment.lower() 
                for x in ['<script', 'javascript:', 'onerror=', 'onload=']) else 'COMMENT',
            'user_agent': user_agent
        }
        
        # Analyser la menace
        threat_manager.process_log_entry(json.dumps(log_entry))
        
        # Simuler une réponse d'erreur réaliste
        if any(x in comment.lower() for x in ['<script', 'javascript:', 'onerror=', 'onload=']):
            return jsonify({'error': 'Invalid comment content'}), 400
        return jsonify({'status': 'Comment is being reviewed'}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ssh/logs', methods=['GET'])
def get_ssh_logs_v2():
    """
    Retrieve SSH logs with optional filtering
    """
    try:
        # Get query parameters
        log_type = request.args.get('type', 'recent')
        
        # Use existing SSH log parser
        ssh_stats = ssh_parser.get_ssh_stats()
        
        # Transform SSH logs to match frontend expectations
        parsed_logs = []
        
        # Select logs based on type
        if log_type == 'all':
            # If 'all' is requested, try to get more logs
            logs_to_process = ssh_stats.get('all_commands', ssh_stats.get('recent_commands', []))
        else:
            # Default to recent logs
            logs_to_process = ssh_stats.get('recent_commands', [])
        
        for log in logs_to_process:
            # Robust timestamp parsing
            timestamp = log.get('timestamp', '')
            try:
                # Try multiple timestamp formats
                if isinstance(timestamp, str):
                    # Try ISO format first
                    try:
                        parsed_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        # Fallback to other common formats
                        try:
                            parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                        except (ValueError, TypeError):
                            try:
                                parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                            except (ValueError, TypeError):
                                # If all parsing fails, use current time
                                parsed_timestamp = datetime.now()
                    
                    # Convert to ISO format string
                    formatted_timestamp = parsed_timestamp.isoformat()
                else:
                    # If timestamp is not a string, use current time
                    formatted_timestamp = datetime.now().isoformat()
            except Exception:
                # Absolute fallback
                formatted_timestamp = datetime.now().isoformat()
            
            log_data = {
                'timestamp': formatted_timestamp,
                'username': log.get('username', 'Unknown'),
                'ip_address': log.get('ip', 'Unknown'),
                'session_id': log.get('session_id', None),
                'command': log.get('command', None)
            }
            parsed_logs.append(log_data)
        
        # Sort logs by timestamp in descending order
        parsed_logs.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return jsonify({
            'logs': parsed_logs,
            'total_logs': len(parsed_logs),
            'log_type': log_type
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'logs': [],
            'total_logs': 0,
            'log_type': log_type
        }), 200

@app.route('/api/ssh-logs', methods=['GET'])
def get_ssh_logs_alias():
    return get_ssh_logs_v2()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
