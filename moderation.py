"""
Module de modération pour Smiity Bot
Commandes de modération avec réponses en français
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional

from embeds import EmbedBuilder

class ModerationCog(commands.Cog):
    """Cog pour les commandes de modération"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="Expulse un membre du serveur")
    @app_commands.describe(
        member="Le membre à expulser",
        reason="Raison de l'expulsion"
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = "Aucune raison fournie"):
        """Commande pour expulser un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.kick_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission d'expulser des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérification de la hiérarchie des rôles
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = EmbedBuilder.error(
                "Hiérarchie insuffisante",
                "Vous ne pouvez pas expulser ce membre car il a un rôle supérieur ou égal au vôtre."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérification que le bot peut expulser ce membre
        if member.top_role >= interaction.guild.me.top_role:
            embed = EmbedBuilder.error(
                "Impossible d'expulser",
                "Je ne peux pas expulser ce membre car il a un rôle supérieur au mien."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Envoi d'un message privé au membre avant l'expulsion
            try:
                dm_embed = EmbedBuilder.warning(
                    f"Expulsé de {interaction.guild.name}",
                    f"**Raison:** {reason}\n**Modérateur:** {interaction.user.mention}"
                )
                await member.send(embed=dm_embed)
            except:
                pass  # Ignore si on ne peut pas envoyer de MP
            
            # Expulsion du membre
            await member.kick(reason=f"{reason} | Par {interaction.user}")
            
            # Log de l'action
            await self._log_moderation_action(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "kick",
                reason
            )
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Membre expulsé",
                f"✅ {member.mention} a été expulsé du serveur.\n**Raison:** {reason}"
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error(
                "Permission insuffisante",
                "Je n'ai pas les permissions nécessaires pour expulser ce membre."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite lors de l'expulsion: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ban", description="Bannit un membre du serveur")
    @app_commands.describe(
        member="Le membre à bannir",
        reason="Raison du bannissement",
        delete_messages="Supprimer les messages des X derniers jours (0-7)"
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Aucune raison fournie",
        delete_messages: Optional[int] = 0
    ):
        """Commande pour bannir un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission de bannir des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérification de la hiérarchie des rôles
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = EmbedBuilder.error(
                "Hiérarchie insuffisante",
                "Vous ne pouvez pas bannir ce membre car il a un rôle supérieur ou égal au vôtre."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validation du paramètre delete_messages
        if delete_messages < 0 or delete_messages > 7:
            delete_messages = 0
        
        try:
            # Envoi d'un message privé au membre avant le bannissement
            try:
                dm_embed = EmbedBuilder.error(
                    f"Banni de {interaction.guild.name}",
                    f"**Raison:** {reason}\n**Modérateur:** {interaction.user.mention}"
                )
                await member.send(embed=dm_embed)
            except:
                pass
            
            # Bannissement du membre
            await member.ban(
                reason=f"{reason} | Par {interaction.user}",
                delete_message_days=delete_messages
            )
            
            # Log de l'action
            await self._log_moderation_action(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "ban",
                reason
            )
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Membre banni",
                f"✅ {member.mention} a été banni du serveur.\n**Raison:** {reason}"
            )
            if delete_messages > 0:
                embed.add_field(
                    name="Messages supprimés",
                    value=f"Messages des {delete_messages} derniers jours supprimés",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error(
                "Permission insuffisante",
                "Je n'ai pas les permissions nécessaires pour bannir ce membre."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite lors du bannissement: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unban", description="Débannit un utilisateur")
    @app_commands.describe(
        user_id="L'ID de l'utilisateur à débannir",
        reason="Raison du débannissement"
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = "Aucune raison fournie"
    ):
        """Commande pour débannir un utilisateur"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.ban_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission de débannir des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            
            # Vérification que l'utilisateur est banni
            try:
                ban_entry = await interaction.guild.fetch_ban(user)
            except discord.NotFound:
                embed = EmbedBuilder.error(
                    "Utilisateur non banni",
                    "Cet utilisateur n'est pas banni de ce serveur."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Débannissement
            await interaction.guild.unban(user, reason=f"{reason} | Par {interaction.user}")
            
            # Log de l'action
            await self._log_moderation_action(
                interaction.guild.id,
                user.id,
                interaction.user.id,
                "unban",
                reason
            )
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Utilisateur débanni",
                f"✅ {user.mention} a été débanni du serveur.\n**Raison:** {reason}"
            )
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            embed = EmbedBuilder.error(
                "ID invalide",
                "L'ID utilisateur fourni n'est pas valide."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = EmbedBuilder.error(
                "Utilisateur introuvable",
                "Aucun utilisateur trouvé avec cet ID."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite lors du débannissement: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="mute", description="Rend muet un membre")
    @app_commands.describe(
        member="Le membre à rendre muet",
        duration="Durée du mute (ex: 10m, 1h, 1d)",
        reason="Raison du mute"
    )
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: Optional[str] = None,
        reason: Optional[str] = "Aucune raison fournie"
    ):
        """Commande pour rendre muet un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission de rendre muet des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Calcul de la durée
        timeout_until = None
        if duration:
            timeout_until = self._parse_duration(duration)
            if not timeout_until:
                embed = EmbedBuilder.error(
                    "Durée invalide",
                    "Format de durée invalide. Utilisez: 10m, 1h, 1d, etc."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        try:
            # Application du timeout
            await member.timeout(timeout_until, reason=f"{reason} | Par {interaction.user}")
            
            # Log de l'action
            await self._log_moderation_action(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "mute",
                reason,
                duration=duration
            )
            
            # Réponse de confirmation
            duration_text = f" pendant {duration}" if duration else " indéfiniment"
            embed = EmbedBuilder.success(
                "Membre rendu muet",
                f"✅ {member.mention} a été rendu muet{duration_text}.\n**Raison:** {reason}"
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = EmbedBuilder.error(
                "Permission insuffisante",
                "Je n'ai pas les permissions nécessaires pour rendre muet ce membre."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unmute", description="Retire le mute d'un membre")
    @app_commands.describe(
        member="Le membre à démuter",
        reason="Raison du démute"
    )
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Aucune raison fournie"
    ):
        """Commande pour retirer le mute d'un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission de démuter des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Retrait du timeout
            await member.timeout(None, reason=f"{reason} | Par {interaction.user}")
            
            # Log de l'action
            await self._log_moderation_action(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "unmute",
                reason
            )
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Membre démuté",
                f"✅ {member.mention} n'est plus muet.\n**Raison:** {reason}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="warn", description="Avertit un membre")
    @app_commands.describe(
        member="Le membre à avertir",
        reason="Raison de l'avertissement"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        """Commande pour avertir un membre"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous n'avez pas la permission d'avertir des membres."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Log de l'avertissement
            await self._log_moderation_action(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "warn",
                reason
            )
            
            # Envoi d'un message privé au membre
            try:
                dm_embed = EmbedBuilder.warning(
                    f"Avertissement sur {interaction.guild.name}",
                    f"**Raison:** {reason}\n**Modérateur:** {interaction.user.mention}"
                )
                await member.send(embed=dm_embed)
            except:
                pass
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Avertissement donné",
                f"✅ {member.mention} a été averti.\n**Raison:** {reason}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _parse_duration(self, duration_str: str) -> Optional[datetime]:
        """Parse une chaîne de durée et retourne un datetime"""
        try:
            # Extraction du nombre et de l'unité
            import re
            match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
            if not match:
                return None
            
            amount, unit = match.groups()
            amount = int(amount)
            
            # Calcul de la durée
            if unit == 's':
                delta = timedelta(seconds=amount)
            elif unit == 'm':
                delta = timedelta(minutes=amount)
            elif unit == 'h':
                delta = timedelta(hours=amount)
            elif unit == 'd':
                delta = timedelta(days=amount)
            else:
                return None
            
            return datetime.utcnow() + delta
            
        except:
            return None
    
    async def _log_moderation_action(
        self,
        guild_id: int,
        user_id: int,
        moderator_id: int,
        action_type: str,
        reason: str,
        duration: Optional[str] = None
    ):
        """Log une action de modération dans la base de données"""
        try:
            from database.models import Moderation
            
            # Calcul de la date d'expiration pour les mutes temporaires
            expires_at = None
            if action_type == "mute" and duration:
                expires_at = self._parse_duration(duration)
            
            moderation_entry = Moderation(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type=action_type,
                reason=reason,
                duration=self._duration_to_seconds(duration) if duration else None,
                expires_at=expires_at
            )
            
            async with self.bot.db.get_session() as session:
                session.add(moderation_entry)
                await session.commit()
                
        except Exception as e:
            self.bot.logger.error(f"Erreur lors du log de modération: {e}")
    
    def _duration_to_seconds(self, duration_str: str) -> Optional[int]:
        """Convertit une durée en secondes"""
        if not duration_str:
            return None
        
        try:
            import re
            match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
            if not match:
                return None
            
            amount, unit = match.groups()
            amount = int(amount)
            
            if unit == 's':
                return amount
            elif unit == 'm':
                return amount * 60
            elif unit == 'h':
                return amount * 3600
            elif unit == 'd':
                return amount * 86400
            
        except:
            return None

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(ModerationCog(bot))

