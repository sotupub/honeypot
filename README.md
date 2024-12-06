# Honeypot System pour la Nuit de l'Info

Ce projet est un système honeypot conçu pour détecter, surveiller et analyser les tentatives d'attaques sur votre infrastructure.

## Fonctionnalités

- Simulation d'un serveur SSH vulnérable
- Interface web sécurisée pour visualiser les attaques
- Enregistrement des tentatives d'intrusion en temps réel
- Visualisation des données avec graphiques
- Système de blocage automatique des IP malveillantes

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Configurer les paramètres dans `config.py`

3. Lancer le serveur honeypot :
```bash
python server.py
```

4. Lancer l'interface web :
```bash
python web_interface.py
```

## Accès à l'interface

- URL : http://localhost:5000
- Identifiants par défaut :
  - Username : admin
  - Password : secure_password

⚠️ IMPORTANT : Changez les identifiants par défaut avant le déploiement !

## Structure du projet

- `server.py` : Serveur honeypot
- `web_interface.py` : Interface web de visualisation
- `config.py` : Configuration du système
- `templates/` : Templates HTML pour l'interface web
- `honeypot.db` : Base de données SQLite
- `honeypot.log` : Fichier de logs

## Sécurité

- L'interface web est protégée par authentification
- Les mots de passe sont stockés de manière sécurisée
- Les logs sont conservés pour analyse forensique
- Système de blocage automatique des IP malveillantes

## Auteurs

Créé pour le défi GRETA de Grenoble - Nuit de l'Info 2023
