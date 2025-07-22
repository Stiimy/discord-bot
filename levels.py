"""
Module de niveaux pour Smiity Bot
Système XP et niveaux comme MEE6
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import asyncio
import random

from utils.embeds import EmbedBuilder

class LevelsCog(commands.Cog):
    """Cog pour le système de niveaux et XP"""
    
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldowns = {}  # Cache des cooldowns XP
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Événement déclenché à chaque message pour donner de l'XP"""
        
        # Ignorer les bots et les messages privés
        if message.author.bot or not message.guild:
            return
        
        # Vérifier si le système de niveaux est activé
        guild_config = await self.bot.db.get_guild(message.guild.id)
        if not guild_config or not guild_config.levels_enabled:
            return
        
        # Vérifier le cooldown XP
        user_key = f"{message.author.id}_{message.guild.id}"
        now = datetime.utcnow()
        
        if user_key in self.xp_cooldowns:
            if now < self.xp_cooldowns[user_key]:
                return  # Encore en cooldown
        
        # Définir le nouveau cooldown (60 secondes)
        self.xp_cooldowns[user_key] = now + timedelta(seconds=60)
        
        # Donner de l'XP aléatoire (15-25 XP)
        xp_gain = random.randint(15, 25)
        
        try:
            # Ajouter l'XP à l'utilisateur
            level_data = await self.bot.db.add_xp(message.author.id, message.guild.id, xp_gain)
            
            # Vérifier si l'utilisateur a gagné un niveau
            if hasattr(level_data, 'level_up') and level_data.level_up:
                await self._send_level_up_message(message, level_data)
                
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de l'ajout d'XP: {e}")
    
    async def _send_level_up_message(self, message, level_data):
        """Envoie un message de montée de niveau"""
        try:
            embed = EmbedBuilder.level_up(message.author, level_data.level, level_data.xp)
            
            # Envoyer dans le même canal que le message
            await message.channel.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de l'envoi du message de niveau: {e}")
    
    @app_commands.command(name="rank", description="Affiche votre rang ou celui d'un autre membre")
    @app_commands.describe(member="Le membre dont vous voulez voir le rang")
    async def rank(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Commande pour afficher le rang d'un utilisateur"""
        
        target = member or interaction.user
        
        try:
            # Récupération des données de niveau
            level_data = await self.bot.db.get_user_level(target.id, interaction.guild.id)
            
            # Calcul du rang dans le serveur
            rank = await self._get_user_rank(target.id, interaction.guild.id)
            
            # Calcul de l'XP nécessaire pour le prochain niveau
            current_level_xp = self._level_to_xp(level_data.level)
            next_level_xp = self._level_to_xp(level_data.level + 1)
            xp_needed = next_level_xp - level_data.xp
            
            # Création de l'embed
            embed = discord.Embed(
                title=f"📊 Rang de {target.display_name}",
                color=0x7289da,
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            
            embed.add_field(
                name="🏆 Rang",
                value=f"#{rank}",
                inline=True
            )
            
            embed.add_field(
                name="⭐ Niveau",
                value=f"{level_data.level}",
                inline=True
            )
            
            embed.add_field(
                name="💫 XP Total",
                value=f"{level_data.xp:,}",
                inline=True
            )
            
            embed.add_field(
                name="📈 XP pour le niveau suivant",
                value=f"{xp_needed:,} XP",
                inline=True
            )
            
            embed.add_field(
                name="💬 Messages envoyés",
                value=f"{level_data.messages_count:,}",
                inline=True
            )
            
            # Barre de progression
            progress = (level_data.xp - current_level_xp) / (next_level_xp - current_level_xp)
            progress_bar = self._create_progress_bar(progress)
            
            embed.add_field(
                name="📊 Progression",
                value=f"{progress_bar} {progress:.1%}",
                inline=False
            )
            
            embed.set_footer(text="Continuez à être actif pour gagner plus d'XP !")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de récupérer les données de rang: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des niveaux du serveur")
    @app_commands.describe(page="Page du classement à afficher")
    async def leaderboard(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """Commande pour afficher le classement des niveaux"""
        
        if page < 1:
            page = 1
        
        try:
            # Récupération du top des utilisateurs
            top_users = await self._get_top_users(interaction.guild.id, page)
            
            if not top_users:
                embed = EmbedBuilder.info(
                    "Classement vide",
                    "Aucun utilisateur n'a encore gagné d'XP sur ce serveur."
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Création de l'embed de classement
            embed = discord.Embed(
                title="🏆 Classement des niveaux",
                description=f"Top des membres les plus actifs de **{interaction.guild.name}**",
                color=0xffd700,
                timestamp=datetime.utcnow()
            )
            
            leaderboard_text = []
            start_rank = (page - 1) * 10 + 1
            
            for i, user_data in enumerate(top_users, start=start_rank):
                # Récupération du membre Discord
                try:
                    member = interaction.guild.get_member(user_data['user_id'])
                    if member:
                        username = member.display_name
                    else:
                        username = f"Utilisateur {user_data['user_id']}"
                except:
                    username = f"Utilisateur {user_data['user_id']}"
                
                # Emoji de médaille
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                leaderboard_text.append(
                    f"{medal} **{username}** - Niveau {user_data['level']} ({user_data['xp']:,} XP)"
                )
            
            embed.description += f"\n\n" + "\n".join(leaderboard_text)
            embed.set_footer(text=f"Page {page} • Utilisez /leaderboard <page> pour naviguer")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de récupérer le classement: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="setlevel", description="Définit le niveau d'un membre (Modérateurs uniquement)")
    @app_commands.describe(
        member="Le membre dont modifier le niveau",
        level="Le nouveau niveau"
    )
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, level: int):
        """Commande pour définir le niveau d'un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.manage_guild:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous devez avoir la permission **Gérer le serveur** pour utiliser cette commande."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if level < 0 or level > 1000:
            embed = EmbedBuilder.error(
                "Niveau invalide",
                "Le niveau doit être compris entre 0 et 1000."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Calcul de l'XP correspondant au niveau
            new_xp = self._level_to_xp(level)
            
            # Mise à jour dans la base de données
            async with self.bot.db.get_session() as session:
                from database.models import Level
                from sqlalchemy import select, and_
                
                # Récupération ou création de l'entrée de niveau
                result = await session.execute(
                    select(Level).where(
                        and_(Level.user_id == member.id, Level.guild_id == interaction.guild.id)
                    )
                )
                level_entry = result.scalar_one_or_none()
                
                if not level_entry:
                    level_entry = Level(
                        user_id=member.id,
                        guild_id=interaction.guild.id,
                        level=level,
                        xp=new_xp
                    )
                    session.add(level_entry)
                else:
                    level_entry.level = level
                    level_entry.xp = new_xp
                
                await session.commit()
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Niveau modifié",
                f"✅ Le niveau de {member.mention} a été défini à **{level}** ({new_xp:,} XP)."
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de modifier le niveau: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="addxp", description="Ajoute de l'XP à un membre (Modérateurs uniquement)")
    @app_commands.describe(
        member="Le membre à qui ajouter de l'XP",
        amount="Quantité d'XP à ajouter"
    )
    async def addxp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Commande pour ajouter de l'XP à un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.manage_guild:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous devez avoir la permission **Gérer le serveur** pour utiliser cette commande."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount < -1000000 or amount > 1000000:
            embed = EmbedBuilder.error(
                "Quantité invalide",
                "La quantité d'XP doit être comprise entre -1,000,000 et 1,000,000."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Ajout de l'XP
            level_data = await self.bot.db.add_xp(member.id, interaction.guild.id, amount)
            
            # Réponse de confirmation
            action = "ajouté" if amount > 0 else "retiré"
            embed = EmbedBuilder.success(
                "XP modifié",
                f"✅ {abs(amount):,} XP {action} à {member.mention}.\n"
                f"**Nouveau total:** {level_data.xp:,} XP (Niveau {level_data.level})"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de modifier l'XP: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _level_to_xp(self, level: int) -> int:
        """Convertit un niveau en XP requis"""
        return level * level * 100
    
    def _xp_to_level(self, xp: int) -> int:
        """Convertit l'XP en niveau"""
        import math
        return int(math.sqrt(xp / 100))
    
    def _create_progress_bar(self, progress: float, length: int = 20) -> str:
        """Crée une barre de progression visuelle"""
        filled = int(progress * length)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    async def _get_user_rank(self, user_id: int, guild_id: int) -> int:
        """Récupère le rang d'un utilisateur dans le serveur"""
        try:
            async with self.bot.db.get_session() as session:
                from database.models import Level
                from sqlalchemy import select, func
                
                # Compter les utilisateurs avec plus d'XP
                result = await session.execute(
                    select(func.count(Level.user_id)).where(
                        Level.guild_id == guild_id,
                        Level.xp > select(Level.xp).where(
                            Level.user_id == user_id,
                            Level.guild_id == guild_id
                        ).scalar_subquery()
                    )
                )
                
                higher_users = result.scalar() or 0
                return higher_users + 1
                
        except Exception:
            return 1
    
    async def _get_top_users(self, guild_id: int, page: int = 1, limit: int = 10) -> List[Dict]:
        """Récupère le top des utilisateurs par XP"""
        try:
            offset = (page - 1) * limit
            
            async with self.bot.db.get_session() as session:
                from database.models import Level
                from sqlalchemy import select
                
                result = await session.execute(
                    select(Level).where(
                        Level.guild_id == guild_id
                    ).order_by(Level.xp.desc()).offset(offset).limit(limit)
                )
                
                levels = result.scalars().all()
                
                return [
                    {
                        'user_id': level.user_id,
                        'level': level.level,
                        'xp': level.xp,
                        'messages_count': level.messages_count
                    }
                    for level in levels
                ]
                
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de la récupération du top: {e}")
            return []

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(LevelsCog(bot))

