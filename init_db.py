import sqlite3
import os
from config import DATABASE_FILE

def init_database():
    # Supprimer l'ancienne base de données si elle existe
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Ancienne base de données supprimée: {DATABASE_FILE}")

    # Créer une nouvelle base de données
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Créer la table des attaques
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

    # Créer la table des IP bannies
    c.execute('''CREATE TABLE IF NOT EXISTS banned_ips
                (ip_address TEXT PRIMARY KEY,
                 ban_timestamp TEXT,
                 reason TEXT,
                 expires TEXT)''')

    # Créer la table des scores de menace
    c.execute('''CREATE TABLE IF NOT EXISTS threat_scores
                (ip_address TEXT PRIMARY KEY,
                 score INTEGER,
                 last_attack TEXT,
                 attack_count INTEGER,
                 attack_types TEXT)''')

    # Créer la table des patterns d'attaque
    c.execute('''CREATE TABLE IF NOT EXISTS attack_patterns
                (pattern_id TEXT PRIMARY KEY,
                 pattern_type TEXT,
                 pattern_data TEXT,
                 severity INTEGER,
                 created_at TEXT)''')

    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_database()
