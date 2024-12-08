# Documentation du Système Honeypot SSH et Web

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du Système](#architecture-du-système)
3. [Composants Principaux](#composants-principaux)
4. [Fonctionnalités de Détection](#fonctionnalités-de-détection)
5. [Configuration et Installation](#configuration-et-installation)
6. [Surveillance et Alertes](#surveillance-et-alertes)

## Vue d'ensemble

Notre système honeypot est une solution de sécurité complète qui simule deux types de cibles :
- Un serveur SSH vulnérable
- Une interface web avec des vulnérabilités simulées

### Objectifs du Système
- Détecter les tentatives d'intrusion
- Collecter des informations sur les attaquants
- Analyser les méthodes d'attaque
- Générer des alertes en temps réel

## Architecture du Système

### 1. Composant SSH (Port 22222)
```
Attaquant -> Honeypot SSH -> Logs -> Dashboard
```

### 2. Composant Web (Port 6000)
```
Attaquant -> API Web -> Logs -> Dashboard
```

## Composants Principaux

### 1. Serveur SSH Honeypot
- **Port**: 22222
- **Authentification**:
  - Utilisateur: ubuntu / Password: ubuntu123
  - Utilisateur: root / Password: 123456
- **Fonctionnalités**:
  - Simulation d'un système Linux
  - Commandes basiques simulées (ls, cd, pwd, etc.)
  - Logging de toutes les interactions

### 2. Dashboard de Monitoring
- **URL**: http://localhost:6000
- **Fonctionnalités**:
  - Visualisation en temps réel des attaques
  - Statistiques des tentatives de connexion
  - Analyse des patterns d'attaque
  - Interface responsive

## Fonctionnalités de Détection

### 1. Détection SSH
- Tentatives de force brute
- Scan de ports
- Tentatives d'exploitation de vulnérabilités
- Commandes malveillantes

### 2. Détection Web
- Injections SQL
- XSS (Cross-Site Scripting)
- Tentatives de manipulation de paramètres
- Scan de vulnérabilités

## Logs et Surveillance

### Structure des Logs SSH
```json
{
    "timestamp": "2024-12-08T11:28:56Z",
    "ip": "196.203.50.171",
    "username": "ubuntu",
    "command": "ls",
    "session_id": "196.203.50.171-22799-1733656427",
    "type": "command"
}
```

### Emplacement des Logs
- Logs SSH: `/var/log/ssh/access.log`
- Logs Web: Stockés dans la base de données

## Configuration et Installation

### Prérequis
```bash
python3 -m pip install paramiko
python3 -m pip install nextjs
```

### Démarrage du Système
1. Lancer le serveur SSH:
```bash
python3 ssh_server.py
```

2. Lancer le dashboard:
```bash
cd honeypot-dashboard
npm run dev
```

## Surveillance et Alertes

### Types d'Alertes
1. **Alertes Critiques**
   - Tentatives d'accès root
   - Commandes dangereuses
   - Attaques par force brute

2. **Alertes de Surveillance**
   - Nouvelles IP suspectes
   - Patterns d'attaque inhabituels
   - Pics d'activité anormaux

### Dashboard de Monitoring

#### Page d'Attaques
- Visualisation des attaques en temps réel
- Graphiques de distribution des attaques
- Filtres par type d'attaque et période

#### Page SSH Logs
- Liste détaillée des connexions
- Historique des commandes exécutées
- Analyse des sessions suspectes

## Sécurité et Maintenance

### Bonnes Pratiques
1. Vérifier régulièrement les logs
2. Mettre à jour les signatures d'attaque
3. Sauvegarder les données régulièrement
4. Monitorer l'utilisation des ressources

### Limitations
- Simulation limitée des commandes
- Pas d'environnement shell complet
- Ressources système limitées

## Conclusion

Ce honeypot offre une solution complète pour :
- Détecter les tentatives d'intrusion
- Analyser les méthodes d'attaque
- Générer des rapports détaillés
- Améliorer la sécurité globale

Pour toute question ou amélioration, consultez la documentation technique ou contactez l'équipe de sécurité.
