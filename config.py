"""
Module de configuration pour Smiity Bot
"""

import os
from typing import Dict, Any

class Config:
    """Gestionnaire de configuration pour Smiity Bot"""
    
    def __init__(self):
        self.bot_token = os.getenv('DISCORD_TOKEN')
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///smiity_bot.db')
        self.bot_prefix = os.getenv('BOT_PREFIX', '!')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Configuration des couleurs pour les embeds
        self.colors = {
            'success': 0x00ff00,
            'error': 0xff0000,
            'warning': 0xffff00,
            'info': 0x0099ff,
            'primary': 0x7289da
        }
        
        # Configuration des emojis
        self.emojis = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'loading': '⏳',
            'level_up': '🎉',
            'money': '💰',
            'xp': '⭐'
        }
        
        # Configuration des niveaux
        self.level_config = {
            'xp_per_message': 15,
            'xp_cooldown': 60,  # secondes
            'level_up_bonus': 100
        }
        
        # Configuration de l'économie
        self.economy_config = {
            'daily_amount': 100,
            'daily_bonus_streak': 50,
            'max_daily_streak': 7
        }
    
    def get_embed_color(self, color_type: str) -> int:
        """Retourne la couleur d'embed pour un type donné"""
        return self.colors.get(color_type, self.colors['primary'])
    
    def get_emoji(self, emoji_type: str) -> str:
        """Retourne l'emoji pour un type donné"""
        return self.emojis.get(emoji_type, '')
    
    def validate(self) -> bool:
        """Valide la configuration"""
        if not self.bot_token:
            raise ValueError("DISCORD_TOKEN n'est pas défini dans les variables d'environnement")
        
        return True

