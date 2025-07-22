# 📦 Guide d'installation de Smiity Bot

Ce guide vous accompagne pas à pas dans l'installation et la configuration de Smiity Bot sur votre serveur.

## 🔧 Prérequis système

### Système d'exploitation
- **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **Windows** 10/11 avec WSL2 (recommandé) ou Windows natif
- **macOS** 10.15+ (Catalina ou supérieur)

### Logiciels requis
- **Python 3.11 ou supérieur** (obligatoire)
- **Git** pour cloner le repository
- **Base de données** (PostgreSQL recommandé, SQLite par défaut)

### Ressources minimales
- **RAM** : 512 MB minimum, 1 GB recommandé
- **Stockage** : 100 MB pour le bot + espace pour la base de données
- **Réseau** : Connexion internet stable

## 🤖 Création du bot Discord

### Étape 1 : Créer l'application Discord

1. Rendez-vous sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur "New Application"
3. Donnez un nom à votre application (ex: "Smiity Bot")
4. Acceptez les conditions d'utilisation

### Étape 2 : Configurer le bot

1. Dans le menu de gauche, cliquez sur "Bot"
2. Cliquez sur "Add Bot" puis "Yes, do it!"
3. **Copiez le token** (vous en aurez besoin plus tard)
4. Activez les intents suivants :
   - ✅ **Message Content Intent**
   - ✅ **Server Members Intent**
   - ✅ **Presence Intent**

### Étape 3 : Générer le lien d'invitation

1. Allez dans "OAuth2" > "URL Generator"
2. Sélectionnez les scopes :
   - ✅ `bot`
   - ✅ `applications.commands`
3. Sélectionnez les permissions :
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Manage Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Kick Members
   - ✅ Ban Members
   - ✅ Manage Roles
   - ✅ Moderate Members
4. Copiez l'URL générée pour inviter le bot plus tard

## 💻 Installation sur Linux (Ubuntu/Debian)

### Étape 1 : Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

### Étape 2 : Installation de Python 3.11
```bash
# Ubuntu 22.04+ / Debian 12+
sudo apt install python3.11 python3.11-pip python3.11-venv git -y

# Ubuntu 20.04 / Debian 11 (via PPA)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv git -y
```

### Étape 3 : Cloner le projet
```bash
git clone <repository_url>
cd smiity_bot
```

### Étape 4 : Créer un environnement virtuel
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Étape 5 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 6 : Configuration
```bash
cp .env.example .env
nano .env  # Ou votre éditeur préféré
```

Modifiez le fichier `.env` :
```env
DISCORD_TOKEN=votre_token_discord_ici
DATABASE_URL=sqlite+aiosqlite:///smiity_bot.db
BOT_PREFIX=!
DEBUG=False
```

### Étape 7 : Test de fonctionnement
```bash
python main.py
```

## 🪟 Installation sur Windows

### Étape 1 : Installation de Python

1. Téléchargez Python 3.11+ depuis [python.org](https://www.python.org/downloads/)
2. **Important** : Cochez "Add Python to PATH" lors de l'installation
3. Ouvrez PowerShell en tant qu'administrateur
4. Vérifiez l'installation :
```powershell
python --version
pip --version
```

### Étape 2 : Installation de Git

1. Téléchargez Git depuis [git-scm.com](https://git-scm.com/download/win)
2. Installez avec les paramètres par défaut

### Étape 3 : Cloner le projet
```powershell
git clone <repository_url>
cd smiity_bot
```

### Étape 4 : Environnement virtuel
```powershell
python -m venv venv
venv\Scripts\activate
```

### Étape 5 : Installation des dépendances
```powershell
pip install -r requirements.txt
```

### Étape 6 : Configuration
```powershell
copy .env.example .env
notepad .env
```

Modifiez le fichier avec vos paramètres.

### Étape 7 : Lancement
```powershell
python main.py
```

## 🍎 Installation sur macOS

### Étape 1 : Installation d'Homebrew (si pas déjà installé)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Étape 2 : Installation des dépendances
```bash
brew install python@3.11 git
```

### Étape 3 : Cloner et configurer
```bash
git clone <repository_url>
cd smiity_bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Étape 4 : Configuration
```bash
cp .env.example .env
nano .env
```

## 🗄️ Configuration de la base de données

### SQLite (par défaut)
Aucune configuration supplémentaire requise. La base de données sera créée automatiquement.

### PostgreSQL (recommandé pour la production)

#### Installation de PostgreSQL

**Ubuntu/Debian :**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows :**
Téléchargez depuis [postgresql.org](https://www.postgresql.org/download/windows/)

**macOS :**
```bash
brew install postgresql
brew services start postgresql
```

#### Configuration de la base de données

1. Créez un utilisateur et une base de données :
```sql
sudo -u postgres psql
CREATE USER smiity_bot WITH PASSWORD 'votre_mot_de_passe';
CREATE DATABASE smiity_bot OWNER smiity_bot;
GRANT ALL PRIVILEGES ON DATABASE smiity_bot TO smiity_bot;
\q
```

2. Modifiez votre fichier `.env` :
```env
DATABASE_URL=postgresql+asyncpg://smiity_bot:votre_mot_de_passe@localhost/smiity_bot
```

## 🚀 Déploiement en production

### Utilisation de systemd (Linux)

1. Créez un fichier de service :
```bash
sudo nano /etc/systemd/system/smiity-bot.service
```

2. Contenu du fichier :
```ini
[Unit]
Description=Smiity Bot Discord
After=network.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/chemin/vers/smiity_bot
Environment=PATH=/chemin/vers/smiity_bot/venv/bin
ExecStart=/chemin/vers/smiity_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Activez et démarrez le service :
```bash
sudo systemctl daemon-reload
sudo systemctl enable smiity-bot
sudo systemctl start smiity-bot
```

4. Vérifiez le statut :
```bash
sudo systemctl status smiity-bot
```

### Utilisation de PM2 (Node.js requis)

1. Installez PM2 :
```bash
npm install -g pm2
```

2. Créez un fichier `ecosystem.config.js` :
```javascript
module.exports = {
  apps: [{
    name: 'smiity-bot',
    script: 'python',
    args: 'main.py',
    cwd: '/chemin/vers/smiity_bot',
    interpreter: '/chemin/vers/smiity_bot/venv/bin/python',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
```

3. Démarrez avec PM2 :
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🔧 Configuration avancée

### Variables d'environnement complètes

```env
# Configuration Discord (obligatoire)
DISCORD_TOKEN=votre_token_discord

# Base de données
DATABASE_URL=sqlite+aiosqlite:///smiity_bot.db

# Configuration du bot
BOT_PREFIX=!
DEBUG=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/smiity_bot.log

# Sécurité
ENCRYPTION_KEY=votre_clé_de_chiffrement_32_caractères

# Limites
MAX_GUILDS=100
MAX_USERS_PER_GUILD=10000

# Cache
REDIS_URL=redis://localhost:6379/0  # Optionnel
```

### Configuration des logs

Créez le dossier de logs :
```bash
mkdir logs
```

Le bot créera automatiquement les fichiers de logs avec rotation quotidienne.

### Sauvegarde automatique

Script de sauvegarde (`backup.sh`) :
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/chemin/vers/backups"

# Sauvegarde de la base de données SQLite
cp smiity_bot.db "$BACKUP_DIR/smiity_bot_$DATE.db"

# Sauvegarde PostgreSQL (si utilisé)
# pg_dump -U smiity_bot smiity_bot > "$BACKUP_DIR/smiity_bot_$DATE.sql"

# Nettoyage des anciennes sauvegardes (garde 7 jours)
find "$BACKUP_DIR" -name "smiity_bot_*.db" -mtime +7 -delete
```

Ajoutez à crontab pour automatiser :
```bash
crontab -e
# Ajouter : 0 2 * * * /chemin/vers/backup.sh
```

## 🔍 Dépannage

### Problèmes courants

#### Le bot ne se connecte pas
- Vérifiez que le token Discord est correct
- Assurez-vous que les intents sont activés
- Vérifiez votre connexion internet

#### Erreurs de base de données
```bash
# Vérifiez les permissions
ls -la smiity_bot.db

# Recréez la base de données
rm smiity_bot.db
python main.py
```

#### Commandes slash non visibles
- Attendez jusqu'à 1 heure pour la synchronisation globale
- Redémarrez le bot
- Vérifiez les permissions du bot sur le serveur

#### Erreurs de permissions
- Vérifiez que le bot a les rôles nécessaires
- Assurez-vous que le rôle du bot est au-dessus des rôles qu'il doit gérer

### Logs de débogage

Activez le mode debug dans `.env` :
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

Consultez les logs :
```bash
tail -f logs/smiity_bot_$(date +%Y%m%d).log
```

### Tests de connectivité

Script de test (`test_connection.py`) :
```python
import asyncio
import os
from dotenv import load_dotenv
import discord

load_dotenv()

async def test_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'✅ Bot connecté : {client.user}')
        print(f'📊 Connecté à {len(client.guilds)} serveurs')
        await client.close()
    
    try:
        await client.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f'❌ Erreur de connexion : {e}')

if __name__ == "__main__":
    asyncio.run(test_bot())
```

## 📞 Support

### Obtenir de l'aide

1. **Documentation** : Consultez le README.md principal
2. **Issues GitHub** : Ouvrez une issue pour les bugs
3. **Logs** : Consultez toujours les logs en cas de problème

### Informations système utiles

Commande pour collecter les informations système :
```bash
echo "=== Informations système ==="
uname -a
python3 --version
pip3 --version
echo "=== Espace disque ==="
df -h
echo "=== Mémoire ==="
free -h
echo "=== Processus bot ==="
ps aux | grep python
```

---

**Installation terminée !** 🎉

Votre bot Smiity Bot est maintenant prêt à être utilisé. N'oubliez pas de l'inviter sur votre serveur Discord avec le lien généré précédemment.

