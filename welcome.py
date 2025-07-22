"""
Module de bienvenue pour Smiity Bot
Messages de bienvenue personnalisés comme MEE6
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime

from utils.embeds import EmbedBuilder

class WelcomeCog(commands.Cog):
    """Cog pour les messages de bienvenue et de départ"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Événement déclenché quand un membre rejoint le serveur"""
        
        try:
            # Récupération de la configuration du serveur
            guild_config = await self.bot.db.get_guild(member.guild.id)
            
            if not guild_config or not guild_config.welcome_enabled or not guild_config.welcome_channel_id:
                return
            
            # Récupération du canal de bienvenue
            welcome_channel = member.guild.get_channel(guild_config.welcome_channel_id)
            if not welcome_channel:
                return
            
            # Création du message de bienvenue
            embed = discord.Embed(
                title="👋 Bienvenue !",
                description=f"Bienvenue sur **{member.guild.name}**, {member.mention} !",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="👤 Nouveau membre",
                value=f"{member.display_name}#{member.discriminator}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Membre n°",
                value=f"{member.guild.member_count}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Compte créé le",
                value=f"<t:{int(member.created_at.timestamp())}:D>",
                inline=True
            )
            
            embed.add_field(
                name="📋 Informations importantes",
                value=(
                    "• Lisez les règles du serveur\n"
                    "• Présentez-vous si vous le souhaitez\n"
                    "• N'hésitez pas à poser des questions !"
                ),
                inline=False
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"ID: {member.id}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            await welcome_channel.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de l'envoi du message de bienvenue: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Événement déclenché quand un membre quitte le serveur"""
        
        try:
            # Récupération de la configuration du serveur
            guild_config = await self.bot.db.get_guild(member.guild.id)
            
            if not guild_config or not guild_config.welcome_enabled or not guild_config.welcome_channel_id:
                return
            
            # Récupération du canal de bienvenue (utilisé aussi pour les départs)
            welcome_channel = member.guild.get_channel(guild_config.welcome_channel_id)
            if not welcome_channel:
                return
            
            # Création du message de départ
            embed = discord.Embed(
                title="👋 Au revoir !",
                description=f"**{member.display_name}** a quitté le serveur.",
                color=0xff6b6b,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="👤 Membre parti",
                value=f"{member.display_name}#{member.discriminator}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Membres restants",
                value=f"{member.guild.member_count}",
                inline=True
            )
            
            # Calcul du temps passé sur le serveur
            if member.joined_at:
                time_on_server = datetime.utcnow() - member.joined_at.replace(tzinfo=None)
                days = time_on_server.days
                
                embed.add_field(
                    name="⏰ Temps sur le serveur",
                    value=f"{days} jour{'s' if days != 1 else ''}",
                    inline=True
                )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"ID: {member.id}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            await welcome_channel.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de l'envoi du message de départ: {e}")
    
    @app_commands.command(name="welcome", description="Configure les messages de bienvenue")
    @app_commands.describe(
        action="Action à effectuer",
        channel="Canal pour les messages de bienvenue"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Activer", value="enable"),
        app_commands.Choice(name="Désactiver", value="disable"),
        app_commands.Choice(name="Définir le canal", value="set_channel"),
        app_commands.Choice(name="Tester", value="test")
    ])
    async def welcome_config(
        self,
        interaction: discord.Interaction,
        action: str,
        channel: Optional[discord.TextChannel] = None
    ):
        """Commande pour configurer les messages de bienvenue"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.manage_guild:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous devez avoir la permission **Gérer le serveur** pour utiliser cette commande."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Récupération de la configuration
            guild_config = await self.bot.db.get_guild(interaction.guild.id)
            if not guild_config:
                guild_config = await self.bot.db.create_guild(interaction.guild.id, interaction.guild.name)
            
            if action == "enable":
                guild_config.welcome_enabled = True
                
                # Sauvegarde
                async with self.bot.db.get_session() as session:
                    session.add(guild_config)
                    await session.commit()
                
                embed = EmbedBuilder.success(
                    "Messages de bienvenue activés",
                    "Les messages de bienvenue sont maintenant activés !\n"
                    "N'oubliez pas de définir un canal avec `/welcome set_channel`."
                )
                
            elif action == "disable":
                guild_config.welcome_enabled = False
                
                # Sauvegarde
                async with self.bot.db.get_session() as session:
                    session.add(guild_config)
                    await session.commit()
                
                embed = EmbedBuilder.success(
                    "Messages de bienvenue désactivés",
                    "Les messages de bienvenue sont maintenant désactivés."
                )
                
            elif action == "set_channel":
                if not channel:
                    embed = EmbedBuilder.error(
                        "Canal manquant",
                        "Vous devez spécifier un canal pour cette action."
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                guild_config.welcome_channel_id = channel.id
                
                # Sauvegarde
                async with self.bot.db.get_session() as session:
                    session.add(guild_config)
                    await session.commit()
                
                embed = EmbedBuilder.success(
                    "Canal de bienvenue défini",
                    f"Le canal de bienvenue a été défini sur {channel.mention}."
                )
                
            elif action == "test":
                if not guild_config.welcome_channel_id:
                    embed = EmbedBuilder.error(
                        "Canal non configuré",
                        "Vous devez d'abord définir un canal de bienvenue avec `/welcome set_channel`."
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                # Simulation d'un message de bienvenue
                test_embed = discord.Embed(
                    title="👋 Bienvenue ! (Test)",
                    description=f"Bienvenue sur **{interaction.guild.name}**, {interaction.user.mention} !",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                
                test_embed.add_field(
                    name="👤 Nouveau membre",
                    value=f"{interaction.user.display_name}#{interaction.user.discriminator}",
                    inline=True
                )
                
                test_embed.add_field(
                    name="📊 Membre n°",
                    value=f"{interaction.guild.member_count}",
                    inline=True
                )
                
                test_embed.add_field(
                    name="📅 Compte créé le",
                    value=f"<t:{int(interaction.user.created_at.timestamp())}:D>",
                    inline=True
                )
                
                test_embed.add_field(
                    name="📋 Informations importantes",
                    value=(
                        "• Lisez les règles du serveur\n"
                        "• Présentez-vous si vous le souhaitez\n"
                        "• N'hésitez pas à poser des questions !"
                    ),
                    inline=False
                )
                
                test_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                test_embed.set_footer(
                    text=f"ID: {interaction.user.id} • Ceci est un test",
                    icon_url=interaction.guild.icon.url if interaction.guild.icon else None
                )
                
                welcome_channel = interaction.guild.get_channel(guild_config.welcome_channel_id)
                if welcome_channel:
                    await welcome_channel.send(embed=test_embed)
                    
                    embed = EmbedBuilder.success(
                        "Test envoyé",
                        f"Un message de test a été envoyé dans {welcome_channel.mention}."
                    )
                else:
                    embed = EmbedBuilder.error(
                        "Canal introuvable",
                        "Le canal de bienvenue configuré n'existe plus."
                    )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Une erreur s'est produite: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="membercount", description="Affiche le nombre de membres du serveur")
    async def membercount(self, interaction: discord.Interaction):
        """Commande pour afficher les statistiques des membres"""
        
        guild = interaction.guild
        
        # Comptage des différents types de membres
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        online_members = len([m for m in guild.members if m.status != discord.Status.offline and not m.bot])
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {guild.name}",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👥 Total des membres",
            value=f"{total_members:,}",
            inline=True
        )
        
        embed.add_field(
            name="👤 Humains",
            value=f"{humans:,}",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bots",
            value=f"{bots:,}",
            inline=True
        )
        
        embed.add_field(
            name="🟢 En ligne",
            value=f"{online_members:,}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Serveur créé le",
            value=f"<t:{int(guild.created_at.timestamp())}:D>",
            inline=True
        )
        
        # Calcul de l'âge du serveur
        server_age = datetime.utcnow() - guild.created_at.replace(tzinfo=None)
        embed.add_field(
            name="🎂 Âge du serveur",
            value=f"{server_age.days} jours",
            inline=True
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"ID du serveur: {guild.id}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(WelcomeCog(bot))

