# 🚀 Guide de déploiement - Smiity Bot

Ce guide vous accompagne dans le déploiement de Smiity Bot en production sur différentes plateformes.

## 🏗️ Préparation au déploiement

### Checklist pré-déploiement

- [ ] Bot testé en local avec succès
- [ ] Token Discord configuré et fonctionnel
- [ ] Base de données configurée et accessible
- [ ] Variables d'environnement définies
- [ ] Logs configurés
- [ ] Sauvegarde automatique planifiée
- [ ] Monitoring mis en place

### Configuration de production

Créez un fichier `.env.production` :

```env
# Configuration Discord
DISCORD_TOKEN=votre_token_discord_production

# Base de données (PostgreSQL recommandé)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/smiity_bot

# Configuration du bot
BOT_PREFIX=!
DEBUG=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/smiity-bot/smiity_bot.log

# Sécurité
ENCRYPTION_KEY=votre_clé_32_caractères_très_sécurisée

# Limites de production
MAX_GUILDS=1000
MAX_USERS_PER_GUILD=50000

# Cache (optionnel mais recommandé)
REDIS_URL=redis://localhost:6379/0
```

## 🐧 Déploiement sur serveur Linux (VPS/Dédié)

### Méthode 1 : Systemd (Recommandée)

#### 1. Préparation de l'environnement

```bash
# Création de l'utilisateur dédié
sudo useradd -r -s /bin/false smiity-bot
sudo mkdir -p /opt/smiity-bot
sudo mkdir -p /var/log/smiity-bot
sudo chown smiity-bot:smiity-bot /var/log/smiity-bot

# Copie des fichiers
sudo cp -r /chemin/vers/smiity_bot/* /opt/smiity-bot/
sudo chown -R smiity-bot:smiity-bot /opt/smiity-bot
```

#### 2. Installation des dépendances

```bash
cd /opt/smiity-bot
sudo -u smiity-bot python3.11 -m venv venv
sudo -u smiity-bot venv/bin/pip install -r requirements.txt
```

#### 3. Configuration du service systemd

Créez `/etc/systemd/system/smiity-bot.service` :

```ini
[Unit]
Description=Smiity Bot Discord
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=smiity-bot
Group=smiity-bot
WorkingDirectory=/opt/smiity-bot
Environment=PATH=/opt/smiity-bot/venv/bin
EnvironmentFile=/opt/smiity-bot/.env.production
ExecStart=/opt/smiity-bot/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/smiity-bot /var/log/smiity-bot

# Limites de ressources
LimitNOFILE=65536
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

#### 4. Activation et démarrage

```bash
sudo systemctl daemon-reload
sudo systemctl enable smiity-bot
sudo systemctl start smiity-bot

# Vérification
sudo systemctl status smiity-bot
sudo journalctl -u smiity-bot -f
```

### Méthode 2 : Docker

#### 1. Dockerfile

Créez un `Dockerfile` :

```dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="votre@email.com"
LABEL description="Smiity Bot - Discord Bot"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Création de l'utilisateur non-root
RUN groupadd -r smiity && useradd -r -g smiity smiity

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Changement de propriétaire
RUN chown -R smiity:smiity /app

# Utilisateur non-root
USER smiity

# Port exposé (si nécessaire pour monitoring)
EXPOSE 8080

# Commande de démarrage
CMD ["python", "main.py"]
```

#### 2. Docker Compose

Créez un `docker-compose.yml` :

```yaml
version: '3.8'

services:
  smiity-bot:
    build: .
    container_name: smiity-bot
    restart: unless-stopped
    env_file:
      - .env.production
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
    networks:
      - smiity-network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    container_name: smiity-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: smiity_bot
      POSTGRES_USER: smiity_bot
      POSTGRES_PASSWORD: votre_mot_de_passe_sécurisé
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - smiity-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smiity_bot"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: smiity-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - smiity-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  redis_data:

networks:
  smiity-network:
    driver: bridge
```

#### 3. Déploiement Docker

```bash
# Construction et démarrage
docker-compose up -d

# Vérification
docker-compose ps
docker-compose logs -f smiity-bot

# Mise à jour
docker-compose pull
docker-compose up -d --build
```

## ☁️ Déploiement Cloud

### Heroku

#### 1. Préparation des fichiers

Créez un `Procfile` :
```
worker: python main.py
```

Créez un `runtime.txt` :
```
python-3.11.6
```

#### 2. Configuration Heroku

```bash
# Installation Heroku CLI et connexion
heroku login

# Création de l'application
heroku create votre-smiity-bot

# Configuration des variables
heroku config:set DISCORD_TOKEN=votre_token
heroku config:set DATABASE_URL=postgresql://...

# Ajout de PostgreSQL
heroku addons:create heroku-postgresql:mini

# Déploiement
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Vérification
heroku logs --tail
```

### Railway

#### 1. Configuration

Créez un `railway.toml` :
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python main.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### 2. Déploiement

```bash
# Installation Railway CLI
npm install -g @railway/cli

# Connexion et déploiement
railway login
railway init
railway up
```

### DigitalOcean App Platform

#### 1. Configuration

Créez un `.do/app.yaml` :
```yaml
name: smiity-bot
services:
- name: worker
  source_dir: /
  github:
    repo: votre-username/smiity-bot
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DISCORD_TOKEN
    value: votre_token
    type: SECRET
databases:
- name: smiity-db
  engine: PG
  version: "15"
```

## 🔧 Configuration avancée

### Reverse Proxy avec Nginx

Si vous ajoutez une interface web, configurez Nginx :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

### Monitoring avec Prometheus

Ajoutez des métriques dans votre bot :

```python
from prometheus_client import Counter, Histogram, start_http_server

# Métriques
COMMANDS_TOTAL = Counter('bot_commands_total', 'Total commands executed', ['command'])
COMMAND_DURATION = Histogram('bot_command_duration_seconds', 'Command execution time')

# Dans votre bot
start_http_server(8080)  # Port pour les métriques
```

## 📊 Monitoring et logs

### Configuration des logs

Créez `/etc/logrotate.d/smiity-bot` :
```
/var/log/smiity-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 smiity-bot smiity-bot
    postrotate
        systemctl reload smiity-bot
    endscript
}
```

### Monitoring avec Grafana

Dashboard JSON pour Grafana :
```json
{
  "dashboard": {
    "title": "Smiity Bot Monitoring",
    "panels": [
      {
        "title": "Commands per minute",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(bot_commands_total[1m])"
          }
        ]
      }
    ]
  }
}
```

### Alertes Discord

Script d'alerte (`alert.py`) :
```python
import requests
import json

def send_alert(webhook_url, message):
    data = {
        "content": f"🚨 **ALERTE SMIITY BOT** 🚨\n{message}",
        "username": "Monitoring"
    }
    requests.post(webhook_url, json=data)

# Utilisation
send_alert("https://discord.com/api/webhooks/...", "Bot déconnecté!")
```

## 🔄 Mise à jour et maintenance

### Script de mise à jour

Créez `update.sh` :
```bash
#!/bin/bash
set -e

echo "🔄 Mise à jour de Smiity Bot..."

# Sauvegarde
echo "📦 Sauvegarde de la base de données..."
pg_dump smiity_bot > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Arrêt du service
echo "⏹️ Arrêt du service..."
sudo systemctl stop smiity-bot

# Mise à jour du code
echo "📥 Téléchargement des mises à jour..."
git pull origin main

# Mise à jour des dépendances
echo "📦 Mise à jour des dépendances..."
venv/bin/pip install -r requirements.txt --upgrade

# Migration de la base de données (si nécessaire)
echo "🗄️ Migration de la base de données..."
venv/bin/alembic upgrade head

# Redémarrage
echo "▶️ Redémarrage du service..."
sudo systemctl start smiity-bot

# Vérification
echo "✅ Vérification du statut..."
sleep 5
sudo systemctl status smiity-bot

echo "🎉 Mise à jour terminée!"
```

### Sauvegarde automatique

Script de sauvegarde (`backup.sh`) :
```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/smiity-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Sauvegarde PostgreSQL
pg_dump -U smiity_bot smiity_bot | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Sauvegarde des fichiers de configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /opt/smiity-bot/.env.production

# Nettoyage (garde 30 jours)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

# Upload vers S3 (optionnel)
# aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://votre-bucket/backups/
```

Ajout à crontab :
```bash
# Sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/scripts/backup.sh
```

## 🔒 Sécurité en production

### Pare-feu

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### Fail2Ban

Configuration `/etc/fail2ban/jail.local` :
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
```

### Rotation des tokens

Script de rotation (`rotate_token.py`) :
```python
import os
import requests
from dotenv import load_dotenv, set_key

def rotate_discord_token():
    # Logique de rotation du token Discord
    # (nécessite l'API Discord)
    pass

def update_env_file(new_token):
    set_key('.env.production', 'DISCORD_TOKEN', new_token)
    os.system('sudo systemctl restart smiity-bot')

if __name__ == "__main__":
    rotate_discord_token()
```

## 📈 Optimisation des performances

### Configuration PostgreSQL

Optimisations dans `postgresql.conf` :
```ini
# Mémoire
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Connexions
max_connections = 100

# Logs
log_statement = 'mod'
log_min_duration_statement = 1000
```

### Cache Redis

Configuration Redis (`redis.conf`) :
```ini
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Optimisations Python

Dans votre bot, ajoutez :
```python
import asyncio
import uvloop  # Plus rapide que l'event loop par défaut

# Utilisation d'uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

## 🚨 Dépannage en production

### Commandes de diagnostic

```bash
# Statut du service
sudo systemctl status smiity-bot

# Logs en temps réel
sudo journalctl -u smiity-bot -f

# Utilisation des ressources
htop
iotop
nethogs

# Connexions réseau
netstat -tulpn | grep python

# Espace disque
df -h
du -sh /opt/smiity-bot/*
```

### Problèmes courants

#### Bot déconnecté
```bash
# Vérifier les logs
sudo journalctl -u smiity-bot --since "1 hour ago"

# Redémarrer le service
sudo systemctl restart smiity-bot
```

#### Base de données lente
```sql
-- Analyser les requêtes lentes
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### Mémoire insuffisante
```bash
# Vérifier l'utilisation mémoire
free -h
ps aux --sort=-%mem | head

# Ajuster les limites systemd
sudo systemctl edit smiity-bot
# Ajouter:
# [Service]
# MemoryMax=2G
```

## 📋 Checklist de déploiement

### Avant le déploiement
- [ ] Tests complets en local
- [ ] Configuration de production validée
- [ ] Sauvegarde de l'environnement actuel
- [ ] Plan de rollback préparé

### Pendant le déploiement
- [ ] Arrêt propre du service existant
- [ ] Déploiement du nouveau code
- [ ] Migration de la base de données
- [ ] Tests de fumée

### Après le déploiement
- [ ] Vérification du statut du service
- [ ] Tests des fonctionnalités critiques
- [ ] Monitoring des métriques
- [ ] Communication aux utilisateurs

---

**Déploiement réussi !** 🎉

Votre Smiity Bot est maintenant en production et prêt à servir vos utilisateurs Discord 24h/24 et 7j/7.

