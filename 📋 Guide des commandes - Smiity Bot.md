# 📋 Guide des commandes - Smiity Bot

Ce guide détaille toutes les commandes disponibles dans Smiity Bot, organisées par catégorie.

## 🛡️ Commandes de modération

### `/kick` - Expulser un membre
**Description :** Expulse un membre du serveur Discord.

**Syntaxe :** `/kick <membre> [raison]`

**Paramètres :**
- `membre` (obligatoire) : Le membre à expulser
- `raison` (optionnel) : Raison de l'expulsion

**Permissions requises :** Expulser des membres

**Exemples :**
```
/kick @Utilisateur
/kick @Utilisateur Spam répété dans le chat
```

**Fonctionnalités :**
- Vérifie la hiérarchie des rôles
- Envoie un message privé au membre avant l'expulsion
- Log l'action dans la base de données
- Affiche une confirmation avec embed

---

### `/ban` - Bannir un membre
**Description :** Bannit un membre du serveur Discord.

**Syntaxe :** `/ban <membre> [raison] [delete_messages]`

**Paramètres :**
- `membre` (obligatoire) : Le membre à bannir
- `raison` (optionnel) : Raison du bannissement
- `delete_messages` (optionnel) : Nombre de jours de messages à supprimer (0-7)

**Permissions requises :** Bannir des membres

**Exemples :**
```
/ban @Utilisateur
/ban @Utilisateur Comportement toxique 1
```

**Fonctionnalités :**
- Vérifie la hiérarchie des rôles
- Supprime les messages récents si spécifié
- Envoie un message privé avant le bannissement
- Log complet de l'action

---

### `/unban` - Débannir un utilisateur
**Description :** Retire le bannissement d'un utilisateur.

**Syntaxe :** `/unban <user_id> [raison]`

**Paramètres :**
- `user_id` (obligatoire) : ID Discord de l'utilisateur à débannir
- `raison` (optionnel) : Raison du débannissement

**Permissions requises :** Bannir des membres

**Exemples :**
```
/unban 123456789012345678
/unban 123456789012345678 Appel accepté
```

**Fonctionnalités :**
- Vérifie que l'utilisateur est effectivement banni
- Log l'action de débannissement
- Confirmation visuelle avec embed

---

### `/mute` - Rendre muet un membre
**Description :** Applique un timeout à un membre (le rend muet).

**Syntaxe :** `/mute <membre> [durée] [raison]`

**Paramètres :**
- `membre` (obligatoire) : Le membre à rendre muet
- `durée` (optionnel) : Durée du mute (ex: 10m, 1h, 1d)
- `raison` (optionnel) : Raison du mute

**Permissions requises :** Modérer les membres

**Exemples :**
```
/mute @Utilisateur
/mute @Utilisateur 30m Flood dans le chat
/mute @Utilisateur 1h Langage inapproprié
```

**Formats de durée acceptés :**
- `s` : secondes (ex: 30s)
- `m` : minutes (ex: 15m)
- `h` : heures (ex: 2h)
- `d` : jours (ex: 1d)

---

### `/unmute` - Retirer le mute
**Description :** Retire le timeout d'un membre.

**Syntaxe :** `/unmute <membre> [raison]`

**Paramètres :**
- `membre` (obligatoire) : Le membre à démuter
- `raison` (optionnel) : Raison du démute

**Permissions requises :** Modérer les membres

**Exemples :**
```
/unmute @Utilisateur
/unmute @Utilisateur Comportement amélioré
```

---

### `/warn` - Avertir un membre
**Description :** Donne un avertissement à un membre.

**Syntaxe :** `/warn <membre> <raison>`

**Paramètres :**
- `membre` (obligatoire) : Le membre à avertir
- `raison` (obligatoire) : Raison de l'avertissement

**Permissions requises :** Modérer les membres

**Exemples :**
```
/warn @Utilisateur Première infraction au règlement
/warn @Utilisateur Hors-sujet répété
```

**Fonctionnalités :**
- Envoie un message privé au membre
- Enregistre l'avertissement en base de données
- Affichage public de l'action

---

## 📈 Commandes de niveaux

### `/rank` - Afficher le rang
**Description :** Affiche le rang et les statistiques d'un membre.

**Syntaxe :** `/rank [membre]`

**Paramètres :**
- `membre` (optionnel) : Le membre dont voir le rang (vous-même par défaut)

**Exemples :**
```
/rank
/rank @Utilisateur
```

**Informations affichées :**
- Rang dans le serveur
- Niveau actuel
- XP total
- XP nécessaire pour le niveau suivant
- Nombre de messages envoyés
- Barre de progression visuelle

---

### `/leaderboard` - Classement des niveaux
**Description :** Affiche le classement des membres les plus actifs.

**Syntaxe :** `/leaderboard [page]`

**Paramètres :**
- `page` (optionnel) : Page du classement à afficher (défaut: 1)

**Exemples :**
```
/leaderboard
/leaderboard 2
```

**Fonctionnalités :**
- Top 10 par page
- Médailles pour les 3 premiers
- Navigation par pages
- Affichage du niveau et XP total

---

### `/setlevel` - Définir le niveau (Modérateurs)
**Description :** Définit manuellement le niveau d'un membre.

**Syntaxe :** `/setlevel <membre> <niveau>`

**Paramètres :**
- `membre` (obligatoire) : Le membre dont modifier le niveau
- `niveau` (obligatoire) : Le nouveau niveau (0-1000)

**Permissions requises :** Gérer le serveur

**Exemples :**
```
/setlevel @Utilisateur 10
/setlevel @Utilisateur 0
```

**Fonctionnalités :**
- Calcule automatiquement l'XP correspondant
- Met à jour la base de données
- Confirmation de l'action

---

### `/addxp` - Ajouter de l'XP (Modérateurs)
**Description :** Ajoute ou retire de l'XP à un membre.

**Syntaxe :** `/addxp <membre> <quantité>`

**Paramètres :**
- `membre` (obligatoire) : Le membre concerné
- `quantité` (obligatoire) : Quantité d'XP à ajouter (peut être négative)

**Permissions requises :** Gérer le serveur

**Exemples :**
```
/addxp @Utilisateur 500
/addxp @Utilisateur -200
```

**Limites :**
- Minimum : -1,000,000 XP
- Maximum : +1,000,000 XP

---

## 💰 Commandes d'économie

### `/balance` - Afficher le solde
**Description :** Affiche le profil économique d'un membre.

**Syntaxe :** `/balance [membre]`

**Paramètres :**
- `membre` (optionnel) : Le membre dont voir le solde

**Exemples :**
```
/balance
/balance @Utilisateur
```

**Informations affichées :**
- Solde du portefeuille
- Argent en banque
- Série quotidienne (daily streak)
- Total des gains et dépenses
- Richesse totale

---

### `/daily` - Récompense quotidienne
**Description :** Récupère la récompense quotidienne.

**Syntaxe :** `/daily`

**Fonctionnalités :**
- Récompense de base : 100 coins
- Bonus de série : +10 coins par jour consécutif (max 100)
- Cooldown : 20 heures
- Série maintenue si récupéré dans les 48h

**Exemple de gains :**
- Jour 1 : 100 coins
- Jour 2 : 110 coins
- Jour 7 : 160 coins
- Jour 10+ : 200 coins (maximum)

---

### `/work` - Travailler
**Description :** Travaille pour gagner des coins.

**Syntaxe :** `/work`

**Fonctionnalités :**
- Cooldown : 1 heure
- Gains variables selon le métier (40-200 coins)
- Métiers aléatoires : développeur, livreur, streamer, etc.
- Descriptions immersives

---

### `/pay` - Donner des coins
**Description :** Transfère des coins à un autre membre.

**Syntaxe :** `/pay <membre> <montant>`

**Paramètres :**
- `membre` (obligatoire) : Le destinataire
- `montant` (obligatoire) : Quantité de coins à donner

**Exemples :**
```
/pay @Ami 100
/pay @Utilisateur 500
```

**Restrictions :**
- Impossible de se payer soi-même
- Impossible de payer un bot
- Montant doit être positif
- Solde suffisant requis

---

### `/rob` - Voler des coins
**Description :** Tente de voler des coins à un autre membre.

**Syntaxe :** `/rob <membre>`

**Paramètres :**
- `membre` (obligatoire) : La cible du vol

**Exemples :**
```
/rob @Utilisateur
```

**Mécaniques :**
- Chance de succès : 50%
- Minimum requis : 100 coins (voleur) et 50 coins (victime)
- Gains en cas de succès : 10 à 25% du solde de la victime (max 500)
- Amende en cas d'échec : 50 à 25% du solde du voleur (max 200)

---

### `/coinflip` - Pile ou face
**Description :** Parie sur pile ou face.

**Syntaxe :** `/coinflip <choix> <montant>`

**Paramètres :**
- `choix` (obligatoire) : "pile" ou "face"
- `montant` (obligatoire) : Montant à parier

**Exemples :**
```
/coinflip pile 50
/coinflip face 200
```

**Règles :**
- Montant minimum : 1 coin
- Montant maximum : 10,000 coins
- Gains : double de la mise si victoire
- Perte : montant parié si défaite

---

### `/richest` - Classement des plus riches
**Description :** Affiche le classement des membres les plus riches.

**Syntaxe :** `/richest [page]`

**Paramètres :**
- `page` (optionnel) : Page du classement

**Exemples :**
```
/richest
/richest 2
```

**Fonctionnalités :**
- Classement basé sur la richesse totale (portefeuille + banque)
- Top 10 par page
- Médailles pour les 3 premiers

---

## 👋 Commandes de bienvenue

### `/welcome` - Configuration des messages
**Description :** Configure les messages de bienvenue et de départ.

**Syntaxe :** `/welcome <action> [canal]`

**Paramètres :**
- `action` (obligatoire) : "enable", "disable", "set_channel", ou "test"
- `canal` (optionnel) : Canal pour les messages (requis pour "set_channel")

**Permissions requises :** Gérer le serveur

**Exemples :**
```
/welcome enable
/welcome set_channel #général
/welcome test
/welcome disable
```

**Actions disponibles :**
- `enable` : Active les messages de bienvenue
- `disable` : Désactive les messages
- `set_channel` : Définit le canal des messages
- `test` : Envoie un message de test

---

### `/membercount` - Statistiques des membres
**Description :** Affiche les statistiques détaillées du serveur.

**Syntaxe :** `/membercount`

**Informations affichées :**
- Nombre total de membres
- Nombre d'humains et de bots
- Membres en ligne
- Date de création du serveur
- Âge du serveur en jours

---

## 🛠️ Commandes utilitaires

### `/help` - Aide
**Description :** Affiche l'aide du bot ou d'une catégorie spécifique.

**Syntaxe :** `/help [catégorie]`

**Paramètres :**
- `catégorie` (optionnel) : Catégorie d'aide spécifique

**Catégories disponibles :**
- `moderation` : Commandes de modération
- `levels` : Système de niveaux
- `economy` : Commandes d'économie
- `utilities` : Outils utilitaires
- `config` : Configuration du bot

**Exemples :**
```
/help
/help moderation
/help economy
```

---

### `/userinfo` - Informations utilisateur
**Description :** Affiche les informations détaillées d'un membre.

**Syntaxe :** `/userinfo [membre]`

**Paramètres :**
- `membre` (optionnel) : Le membre dont voir les infos

**Informations affichées :**
- Nom d'utilisateur et discriminateur
- ID Discord
- Statut (bot ou humain)
- Date de création du compte
- Date d'arrivée sur le serveur
- Statut actuel (en ligne, absent, etc.)
- Liste des rôles
- Permissions clés

---

### `/serverinfo` - Informations serveur
**Description :** Affiche les informations détaillées du serveur.

**Syntaxe :** `/serverinfo`

**Informations affichées :**
- Nom et ID du serveur
- Propriétaire
- Date de création
- Statistiques des membres
- Nombre de canaux (texte, vocal, catégories)
- Nombre de rôles et d'emojis
- Niveau de boost et nombre de boosts
- Fonctionnalités spéciales (communauté, partenaire, etc.)

---

### `/avatar` - Avatar d'un membre
**Description :** Affiche l'avatar d'un membre en haute résolution.

**Syntaxe :** `/avatar [membre]`

**Paramètres :**
- `membre` (optionnel) : Le membre dont voir l'avatar

**Fonctionnalités :**
- Affichage en haute résolution
- Liens de téléchargement en différents formats (PNG, JPG, WEBP)
- Compatible avec les avatars animés

---

### `/ping` - Latence du bot
**Description :** Affiche la latence du bot et le temps de réponse.

**Syntaxe :** `/ping`

**Informations affichées :**
- Latence WebSocket
- Temps de réponse de l'API
- Indicateur visuel de la qualité de connexion (couleur)

---

### `/embed` - Créer un embed
**Description :** Crée un message embed personnalisé.

**Syntaxe :** `/embed <titre> [description] [couleur]`

**Paramètres :**
- `titre` (obligatoire) : Titre de l'embed
- `description` (optionnel) : Description de l'embed
- `couleur` (optionnel) : Couleur en hexadécimal (ex: #ff0000)

**Permissions requises :** Gérer les messages

**Exemples :**
```
/embed "Annonce importante"
/embed "Événement" "Tournoi ce soir à 20h" #00ff00
```

---

## 🎮 Commandes de divertissement

### `/8ball` - Boule magique
**Description :** Pose une question à la boule magique.

**Syntaxe :** `/8ball <question>`

**Paramètres :**
- `question` (obligatoire) : La question à poser

**Exemples :**
```
/8ball Vais-je gagner au loto ?
/8ball Est-ce que je devrais dormir ?
```

**Réponses possibles :** 19 réponses différentes (positives, neutres, négatives)

---

### `/dice` - Lancer de dés
**Description :** Lance un ou plusieurs dés.

**Syntaxe :** `/dice [faces] [nombre]`

**Paramètres :**
- `faces` (optionnel) : Nombre de faces du dé (2-100, défaut: 6)
- `nombre` (optionnel) : Nombre de dés à lancer (1-10, défaut: 1)

**Exemples :**
```
/dice
/dice 20
/dice 6 3
```

**Fonctionnalités :**
- Affichage des résultats individuels
- Calcul du total pour plusieurs dés
- Support des dés personnalisés

---

### `/choose` - Choix aléatoire
**Description :** Choisit aléatoirement entre plusieurs options.

**Syntaxe :** `/choose <options>`

**Paramètres :**
- `options` (obligatoire) : Options séparées par des virgules

**Exemples :**
```
/choose pizza, burger, sushi
/choose oui, non, peut-être
```

**Limites :**
- Minimum : 2 options
- Maximum : 20 options

---

### `/rps` - Pierre-papier-ciseaux
**Description :** Joue à pierre-papier-ciseaux contre le bot.

**Syntaxe :** `/rps <choix>`

**Paramètres :**
- `choix` (obligatoire) : "pierre", "papier", ou "ciseaux"

**Exemples :**
```
/rps pierre
/rps papier
/rps ciseaux
```

**Règles classiques :**
- Pierre bat ciseaux
- Papier bat pierre
- Ciseaux bat papier

---

### `/quote` - Citation inspirante
**Description :** Génère une citation inspirante aléatoire.

**Syntaxe :** `/quote`

**Fonctionnalités :**
- Base de données de citations célèbres
- Auteurs variés (Einstein, Churchill, Jobs, etc.)
- Affichage élégant avec embed

---

### `/joke` - Blague aléatoire
**Description :** Raconte une blague aléatoire.

**Syntaxe :** `/joke`

**Fonctionnalités :**
- Collection de blagues en français
- Humour varié (jeux de mots, informatique, etc.)
- Nouvelles blagues ajoutées régulièrement

---

### `/compliment` - Complimenter quelqu'un
**Description :** Donne un compliment à un membre.

**Syntaxe :** `/compliment [membre]`

**Paramètres :**
- `membre` (optionnel) : La personne à complimenter

**Exemples :**
```
/compliment
/compliment @Ami
```

**Fonctionnalités :**
- Compliments variés et positifs
- Affichage avec l'avatar du membre
- Ambiance bienveillante

---

### `/meme` - Mème textuel
**Description :** Génère un mème textuel aléatoire.

**Syntaxe :** `/meme`

**Fonctionnalités :**
- Mèmes populaires adaptés en texte
- Références à la culture internet
- Format Discord-friendly

---

## ⚙️ Commandes de configuration

### `/config` - Configuration principale
**Description :** Affiche ou modifie la configuration du bot.

**Syntaxe :** `/config [action] [module] [paramètre] [valeur]`

**Paramètres :**
- `action` (optionnel) : "show", "set", ou "reset"
- `module` (optionnel) : Module à configurer
- `paramètre` (optionnel) : Paramètre à modifier
- `valeur` (optionnel) : Nouvelle valeur

**Permissions requises :** Gérer le serveur

**Actions disponibles :**

#### Afficher la configuration
```
/config show
```

#### Modifier un paramètre
```
/config set moderation enabled true
/config set welcome channel #général
/config set logs channel #logs
```

#### Réinitialiser
```
/config reset
/config reset moderation
```

**Modules configurables :**
- `moderation` : Système de modération
- `levels` : Système de niveaux
- `economy` : Système d'économie
- `welcome` : Messages de bienvenue
- `logs` : Système de logs

**Paramètres par module :**

**Modération :**
- `enabled` : Activer/désactiver (true/false)
- `muted_role` : Rôle de mute (@role ou nom)

**Niveaux :**
- `enabled` : Activer/désactiver (true/false)

**Économie :**
- `enabled` : Activer/désactiver (true/false)

**Bienvenue :**
- `enabled` : Activer/désactiver (true/false)
- `channel` : Canal des messages (#canal ou nom)

**Logs :**
- `enabled` : Activer/désactiver (true/false)
- `channel` : Canal des logs (#canal ou nom)

---

## 🔧 Système automatique

### Gain d'XP automatique
- **Déclencheur :** Envoi d'un message
- **Cooldown :** 60 secondes par utilisateur
- **Gain :** 15-25 XP aléatoire
- **Niveau :** Calculé automatiquement (√(XP/100))
- **Notification :** Message automatique lors des montées de niveau

### Messages de bienvenue/départ
- **Déclencheur :** Arrivée/départ d'un membre
- **Condition :** Module activé et canal configuré
- **Contenu :** Embed avec informations du membre
- **Statistiques :** Nombre de membres, date de création du compte

### Système de logs
- **Actions loggées :** Toutes les actions de modération
- **Stockage :** Base de données avec horodatage
- **Informations :** Utilisateur, modérateur, raison, durée

---

## 📊 Limites et restrictions

### Limites générales
- **Cooldowns :** Respecter les temps d'attente
- **Permissions :** Vérification automatique des droits
- **Hiérarchie :** Impossible de modérer un rang supérieur

### Limites économiques
- **Daily :** 20 heures de cooldown
- **Work :** 1 heure de cooldown
- **Rob :** Soldes minimums requis
- **Coinflip :** Maximum 10,000 coins par pari

### Limites techniques
- **XP :** Maximum 1,000,000 par ajout manuel
- **Niveau :** Maximum 1,000
- **Mute :** Durée maximale selon Discord
- **Embed :** Limites de caractères Discord

---

## 🎯 Conseils d'utilisation

### Pour les modérateurs
1. Configurez d'abord les canaux avec `/config`
2. Testez les fonctionnalités avec `/welcome test`
3. Utilisez `/help moderation` pour les détails
4. Vérifiez les permissions du bot régulièrement

### Pour les utilisateurs
1. Utilisez `/help` pour découvrir les commandes
2. Consultez `/rank` pour suivre votre progression
3. Récupérez votre `/daily` quotidiennement
4. Participez aux activités pour gagner de l'XP

### Bonnes pratiques
- Lisez les descriptions des commandes
- Respectez les cooldowns
- Utilisez les commandes dans les bons canaux
- Signalez les bugs aux administrateurs

---

**Guide complet des commandes Smiity Bot** 📚

*Toutes les commandes sont des slash commands (/). Tapez `/` dans Discord pour voir la liste complète avec l'autocomplétion.*

