#!/usr/bin/env python3
"""
Smiity Bot - Bot Discord multifonctionnel
Bot Discord multifonctionnel avec commandes SLASH en anglais et réponses en français
"""

import os
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import Database
from config import Config
from logger import setup_logger

# Chargement des variables d'environnement
load_dotenv()

class SmiityBot(commands.Bot):
    """Bot principal Smiity Bot"""
    
    def __init__(self):
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv('BOT_PREFIX', '!')),
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.config = Config()
        self.db: Optional[Database] = None
        self.logger = setup_logger()
        
    async def setup_hook(self):
        """Configuration initiale du bot"""
        self.logger.info("🚀 Démarrage de Smiity Bot...")
        
        # Initialisation de la base de données
        self.db = Database(os.getenv('DATABASE_URL', 'sqlite:///smiity_bot.db'))
        await self.db.initialize()
        
        # Chargement des cogs (modules)
        await self.load_cogs()
        
        # Synchronisation des commandes SLASH
        try:
            synced = await self.tree.sync()
            self.logger.info(f"✅ {len(synced)} commandes SLASH synchronisées")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la synchronisation des commandes: {e}")
    
    async def load_cogs(self):
        """Chargement de tous les modules (cogs)"""
        cogs = [
            'panel',
            'extra_cmds',
            'more_cmds',
            'music',
            'automod',
            'reaction_roles',
            'giveaways',
            'logs',
            'tickets',
            'voice_temp',
            'extras',
            'moderation',
            'levels',
            'economy',
            'welcome',
            'utilities',
            'fun'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                self.logger.info(f"✅ Module {cog} chargé")
            except Exception as e:
                self.logger.error(f"❌ Erreur lors du chargement de {cog}: {e}")
    
    async def on_ready(self):
        """Événement déclenché quand le bot est prêt"""
        self.logger.info(f"🎉 {self.user} est connecté et prêt!")
        self.logger.info(f"📊 Connecté à {len(self.guilds)} serveurs")
        
        # Définition du statut du bot
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="les serveurs Discord | /help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_guild_join(self, guild):
        """Événement déclenché quand le bot rejoint un serveur"""
        self.logger.info(f"🆕 Ajouté au serveur: {guild.name} (ID: {guild.id})")
        
        # Initialisation des données du serveur dans la base de données
        if self.db:
            await self.db.create_guild(guild.id, guild.name)
    
    async def on_guild_remove(self, guild):
        """Événement déclenché quand le bot quitte un serveur"""
        self.logger.info(f"👋 Retiré du serveur: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Gestion globale des erreurs de commandes"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        self.logger.error(f"Erreur de commande: {error}")
        
        embed = discord.Embed(
            title="❌ Erreur",
            description="Une erreur s'est produite lors de l'exécution de cette commande.",
            color=discord.Color.red()
        )
        
        try:
            await ctx.respond(embed=embed, ephemeral=True)
        except:
            pass

async def main():
    """Fonction principale"""
    bot = SmiityBot()
    
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        bot.logger.info("🛑 Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        bot.logger.error(f"❌ Erreur fatale: {e}")
    finally:
        if bot.db:
            await bot.db.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())

