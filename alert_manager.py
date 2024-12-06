import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime
from config import ALERT_SETTINGS
from logger import honeypot_logger

class AlertManager:
    def __init__(self):
        self.email_enabled = ALERT_SETTINGS['email_enabled']
        self.telegram_enabled = ALERT_SETTINGS['telegram_enabled']
        
    def format_alert_message(self, alert_type, details):
        """Formate le message d'alerte"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"""
🚨 HONEYPOT ALERT 🚨
Type: {alert_type}
Time: {timestamp}

Details:
{json.dumps(details, indent=2)}

This is an automated alert from your honeypot system.
"""
        return message

    def send_email_alert(self, subject, message):
        """Envoie une alerte par email"""
        if not self.email_enabled:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = 'honeypot@yourdomain.com'
            msg['To'] = ALERT_SETTINGS['email_recipient']
            msg['Subject'] = f"🚨 Honeypot Alert: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Configuration du serveur SMTP (à adapter selon votre configuration)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            # server.login('your_email@gmail.com', 'your_password')  # À configurer
            server.send_message(msg)
            server.quit()
            
            honeypot_logger.info(f"Email alert sent: {subject}")
        except Exception as e:
            honeypot_logger.error(f"Failed to send email alert: {str(e)}")

    def send_telegram_alert(self, message):
        """Envoie une alerte via Telegram"""
        if not self.telegram_enabled:
            return
            
        try:
            bot_token = ALERT_SETTINGS['telegram_bot_token']
            chat_id = ALERT_SETTINGS['telegram_chat_id']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data)
            if response.status_code == 200:
                honeypot_logger.info("Telegram alert sent successfully")
            else:
                honeypot_logger.error(f"Failed to send Telegram alert: {response.text}")
        except Exception as e:
            honeypot_logger.error(f"Failed to send Telegram alert: {str(e)}")

    def alert(self, alert_type, details):
        """Envoie une alerte via tous les canaux configurés"""
        message = self.format_alert_message(alert_type, details)
        
        if self.email_enabled:
            self.send_email_alert(alert_type, message)
            
        if self.telegram_enabled:
            self.send_telegram_alert(message)
            
        # Log l'alerte
        honeypot_logger.warning(f"Alert generated - Type: {alert_type}, Details: {json.dumps(details)}")

class AlertTypes:
    """Types d'alertes prédéfinis"""
    BRUTE_FORCE = "Brute Force Attack"
    SQL_INJECTION = "SQL Injection Attempt"
    COMMAND_INJECTION = "Command Injection Attempt"
    XSS = "Cross-Site Scripting Attempt"
    VULNERABILITY_SCAN = "Vulnerability Scan Detected"
    SUSPICIOUS_IP = "Suspicious IP Activity"
    BANNED_IP = "IP Address Banned"
    HIGH_TRAFFIC = "Unusual High Traffic"
    SERVICE_ATTACK = "Service-Specific Attack"
    SYSTEM_ERROR = "System Error"
