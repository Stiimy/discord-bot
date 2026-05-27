"""
Module pour la création d'embeds Discord pour Smiity Bot
"""

import discord
from datetime import datetime
from typing import Optional, List, Dict, Any

class EmbedBuilder:
    """Constructeur d'embeds pour Smiity Bot"""
    
    @staticmethod
    def success(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Crée un embed de succès"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        return EmbedBuilder._add_footer(embed, **kwargs)
    
    @staticmethod
    def error(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Crée un embed d'erreur"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        return EmbedBuilder._add_footer(embed, **kwargs)
    
    @staticmethod
    def warning(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Crée un embed d'avertissement"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=0xffff00,
            timestamp=datetime.utcnow()
        )
        return EmbedBuilder._add_footer(embed, **kwargs)
    
    @staticmethod
    def info(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Crée un embed d'information"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x0099ff,
            timestamp=datetime.utcnow()
        )
        return EmbedBuilder._add_footer(embed, **kwargs)
    
    @staticmethod
    def config(guild_name: str, config_data: Dict[str, Any]) -> discord.Embed:
        """Crée un embed de configuration
        embed = discord.Embed(
            title=f"⚙️ Configuration de Smiity Bot",
            description=f"Configuration pour **{guild_name}**",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        # Modules principaux
        modules_status = []
        for module, enabled in config_data.get('modules', {}).items():
            status = "🟢 Activé" if enabled else "🔴 Désactivé"
            modules_status.append(f"**{module.title()}**: {status}")
        
        if modules_status:
            embed.add_field(
                name="📋 Modules",
                value="\n".join(modules_status),
                inline=False
            )
        
        # Canaux configurés
        channels = config_data.get('channels', {})
        if channels:
            channel_list = []
            for channel_type, channel_id in channels.items():
                if channel_id:
                    channel_list.append(f"**{channel_type.title()}**: <#{channel_id}>")
                else:
                    channel_list.append(f"**{channel_type.title()}**: Non configuré")
            
            embed.add_field(
                name="📺 Canaux",
                value="\n".join(channel_list),
                inline=True
            )
        
        # Rôles configurés
        roles = config_data.get('roles', {})
        if roles:
            role_list = []
            for role_type, role_id in roles.items():
                if role_id:
                    role_list.append(f"**{role_type.title()}**: <@&{role_id}>")
                else:
                    role_list.append(f"**{role_type.title()}**: Non configuré")
            
            embed.add_field(
                name="👥 Rôles",
                value="\n".join(role_list),
                inline=True
            )
        
        embed.set_footer(
            text="Utilisez /config set <module> <paramètre> <valeur> pour modifier • Smiity Bot",
            icon_url="https://cdn.discordapp.com/app-icons/123456789/icon.png"
        )
        
        return embed
    
    @staticmethod
    def level_up(user: discord.Member, level: int, xp: int) -> discord.Embed:
        """Crée un embed de montée de niveau"""
        embed = discord.Embed(
            title="🎉 Niveau supérieur !",
            description=f"Félicitations {user.mention} ! Vous avez atteint le **niveau {level}** !",
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⭐ XP Total",
            value=f"{xp:,} XP",
            inline=True
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Continuez à être actif pour gagner plus d'XP !")
        
        return embed
    
    @staticmethod
    def leaderboard(guild_name: str, users_data: List[Dict], page: int = 1) -> discord.Embed:
        """Crée un embed de classement"""
        embed = discord.Embed(
            title="🏆 Classement des niveaux",
            description=f"Top des membres les plus actifs de **{guild_name}**",
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        leaderboard_text = []
        for i, user_data in enumerate(users_data, start=(page - 1) * 10 + 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text.append(
                f"{medal} **{user_data['username']}** - Niveau {user_data['level']} ({user_data['xp']:,} XP)"
            )
        
        embed.description += f"\n\n" + "\n".join(leaderboard_text)
        embed.set_footer(text=f"Page {page} • Utilisez /leaderboard <page> pour naviguer")
        
        return embed
    
    @staticmethod
    def economy_profile(user: discord.Member, balance: int, bank: int, daily_streak: int) -> discord.Embed:
        """Crée un embed de profil économique"""
        embed = discord.Embed(
            title=f"💰 Profil économique de {user.display_name}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="💵 Portefeuille",
            value=f"{balance:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🏦 Banque",
            value=f"{bank:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Série quotidienne",
            value=f"{daily_streak} jours",
            inline=True
        )
        
        total = balance + bank
        embed.add_field(
            name="💎 Total",
            value=f"{total:,} coins",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Utilisez /daily pour récupérer votre récompense quotidienne !")
        
        return embed
    
    @staticmethod
    def _add_footer(embed: discord.Embed, footer_text: str = None, **kwargs) -> discord.Embed:
        """Ajoute un pied de page à l'embed"""
        if not footer_text:
            footer_text = "Smiity Bot"
        
        embed.set_footer(
            text=footer_text,
            icon_url=kwargs.get('footer_icon')
        )
        
        return embed

