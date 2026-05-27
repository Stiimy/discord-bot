"""
Module utilitaires pour Smiity Bot
Commandes utilitaires diverses
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union
from datetime import datetime
import asyncio

from embeds import EmbedBuilder

class UtilitiesCog(commands.Cog):
    """Cog pour les commandes utilitaires"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Affiche l'aide du bot")
    @app_commands.describe(category="Catégorie d'aide spécifique")
    @app_commands.choices(category=[
        app_commands.Choice(name="Modération", value="moderation"),
        app_commands.Choice(name="Niveaux", value="levels"),
        app_commands.Choice(name="Économie", value="economy"),
        app_commands.Choice(name="Utilitaires", value="utilities"),
        app_commands.Choice(name="Configuration", value="config")
    ])
    async def help(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Commande d'aide principale"""
        
        if category:
            embed = self._get_category_help(category)
        else:
            embed = self._get_general_help()
        
        await interaction.response.send_message(embed=embed)
    
    def _get_general_help(self) -> discord.Embed:
        """Retourne l'aide générale"""
        embed = discord.Embed(
            title="🤖 Aide de Smiity Bot",
            description="Smiity Bot est un bot multifonctionnel ",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="⚖️ Modération",
            value="`/kick` `/ban` `/mute` `/warn`\nGestion des membres et sanctions",
            inline=True
        )
        
        embed.add_field(
            name="📈 Niveaux",
            value="`/rank` `/leaderboard` `/setlevel`\nSystème d'XP et de niveaux",
            inline=True
        )
        
        embed.add_field(
            name="💰 Économie",
            value="`/balance` `/daily` `/work` `/pay`\nSystème d'économie avec coins",
            inline=True
        )
        
        embed.add_field(
            name="🛠️ Utilitaires",
            value="`/userinfo` `/serverinfo` `/avatar`\nInformations et outils divers",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value="`/config` `/welcome`\nConfiguration du bot",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Fun",
            value="`/coinflip` `/8ball` `/dice`\nCommandes amusantes",
            inline=True
        )
        
        embed.add_field(
            name="📋 Aide détaillée",
            value="Utilisez `/help <catégorie>` pour plus de détails sur une catégorie spécifique.",
            inline=False
        )
        
        embed.set_footer(text="Smiity Bot • Commandes SLASH uniquement")
        
        return embed
    
    def _get_category_help(self, category: str) -> discord.Embed:
        """Retourne l'aide pour une catégorie spécifique"""
        
        help_data = {
            "moderation": {
                "title": "⚖️ Commandes de Modération",
                "description": "Commandes pour gérer et modérer votre serveur",
                "commands": [
                    ("`/kick <membre> [raison]`", "Expulse un membre du serveur"),
                    ("`/ban <membre> [raison] [jours]`", "Bannit un membre du serveur"),
                    ("`/unban <user_id> [raison]`", "Débannit un utilisateur"),
                    ("`/mute <membre> [durée] [raison]`", "Rend muet un membre"),
                    ("`/unmute <membre> [raison]`", "Retire le mute d'un membre"),
                    ("`/warn <membre> <raison>`", "Avertit un membre")
                ]
            },
            "levels": {
                "title": "📈 Système de Niveaux",
                "description": "Commandes pour le système d'XP et de niveaux",
                "commands": [
                    ("`/rank [membre]`", "Affiche le rang d'un membre"),
                    ("`/leaderboard [page]`", "Affiche le classement des niveaux"),
                    ("`/setlevel <membre> <niveau>`", "Définit le niveau d'un membre"),
                    ("`/addxp <membre> <quantité>`", "Ajoute de l'XP à un membre")
                ]
            },
            "economy": {
                "title": "💰 Système d'Économie",
                "description": "Commandes pour le système d'économie avec coins",
                "commands": [
                    ("`/balance [membre]`", "Affiche le solde d'un membre"),
                    ("`/daily`", "Récupère la récompense quotidienne"),
                    ("`/work`", "Travaille pour gagner des coins"),
                    ("`/pay <membre> <montant>`", "Donne des coins à un membre"),
                    ("`/rob <membre>`", "Tente de voler des coins"),
                    ("`/coinflip <choix> <montant>`", "Parie sur pile ou face"),
                    ("`/richest [page]`", "Classement des plus riches")
                ]
            },
            "utilities": {
                "title": "🛠️ Commandes Utilitaires",
                "description": "Outils et informations diverses",
                "commands": [
                    ("`/userinfo [membre]`", "Informations sur un membre"),
                    ("`/serverinfo`", "Informations sur le serveur"),
                    ("`/avatar [membre]`", "Avatar d'un membre"),
                    ("`/membercount`", "Statistiques des membres"),
                    ("`/ping`", "Latence du bot")
                ]
            },
            "config": {
                "title": "⚙️ Configuration",
                "description": "Commandes de configuration du bot",
                "commands": [
                    ("`/config show`", "Affiche la configuration actuelle"),
                    ("`/config set <module> <paramètre> <valeur>`", "Modifie un paramètre"),
                    ("`/config reset [module]`", "Remet à zéro la configuration"),
                    ("`/welcome <action> [canal]`", "Configure les messages de bienvenue")
                ]
            }
        }
        
        if category not in help_data:
            return self._get_general_help()
        
        data = help_data[category]
        embed = discord.Embed(
            title=data["title"],
            description=data["description"],
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        for command, description in data["commands"]:
            embed.add_field(
                name=command,
                value=description,
                inline=False
            )
        
        embed.set_footer(text="Smiity Bot • Les paramètres entre [] sont optionnels")
        
        return embed
    
    @app_commands.command(name="userinfo", description="Affiche les informations d'un membre")
    @app_commands.describe(member="Le membre dont afficher les informations")
    async def userinfo(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Commande pour afficher les informations d'un membre"""
        
        target = member or interaction.user
        
        embed = discord.Embed(
            title=f"👤 Informations de {target.display_name}",
            color=target.color if target.color != discord.Color.default() else 0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Informations de base
        embed.add_field(
            name="🏷️ Nom d'utilisateur",
            value=f"{target.name}#{target.discriminator}",
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=f"`{target.id}`",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="Oui" if target.bot else "Non",
            inline=True
        )
        
        # Dates importantes
        embed.add_field(
            name="📅 Compte créé le",
            value=f"<t:{int(target.created_at.timestamp())}:D>\n<t:{int(target.created_at.timestamp())}:R>",
            inline=True
        )
        
        if target.joined_at:
            embed.add_field(
                name="📥 A rejoint le serveur",
                value=f"<t:{int(target.joined_at.timestamp())}:D>\n<t:{int(target.joined_at.timestamp())}:R>",
                inline=True
            )
        
        # Statut et activité
        status_emojis = {
            discord.Status.online: "🟢 En ligne",
            discord.Status.idle: "🟡 Absent",
            discord.Status.dnd: "🔴 Ne pas déranger",
            discord.Status.offline: "⚫ Hors ligne"
        }
        
        embed.add_field(
            name="📊 Statut",
            value=status_emojis.get(target.status, "❓ Inconnu"),
            inline=True
        )
        
        # Rôles
        if target.roles[1:]:  # Exclure @everyone
            roles = [role.mention for role in reversed(target.roles[1:])]
            roles_text = " ".join(roles[:10])  # Limiter à 10 rôles
            if len(target.roles) > 11:
                roles_text += f" ... et {len(target.roles) - 11} autres"
            
            embed.add_field(
                name=f"🎭 Rôles ({len(target.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # Permissions clés
        key_perms = []
        if target.guild_permissions.administrator:
            key_perms.append("👑 Administrateur")
        if target.guild_permissions.manage_guild:
            key_perms.append("⚙️ Gérer le serveur")
        if target.guild_permissions.manage_channels:
            key_perms.append("📺 Gérer les canaux")
        if target.guild_permissions.manage_roles:
            key_perms.append("🎭 Gérer les rôles")
        if target.guild_permissions.kick_members:
            key_perms.append("👢 Expulser des membres")
        if target.guild_permissions.ban_members:
            key_perms.append("🔨 Bannir des membres")
        
        if key_perms:
            embed.add_field(
                name="🔑 Permissions clés",
                value="\n".join(key_perms),
                inline=False
            )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Affiche les informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        """Commande pour afficher les informations du serveur"""
        
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🏰 Informations de {guild.name}",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informations de base
        embed.add_field(
            name="🆔 ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        embed.add_field(
            name="👑 Propriétaire",
            value=guild.owner.mention if guild.owner else "Inconnu",
            inline=True
        )
        
        embed.add_field(
            name="📅 Créé le",
            value=f"<t:{int(guild.created_at.timestamp())}:D>\n<t:{int(guild.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Statistiques des membres
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        online = len([m for m in guild.members if m.status != discord.Status.offline and not m.bot])
        
        embed.add_field(
            name="👥 Membres",
            value=f"**Total:** {total_members:,}\n**Humains:** {humans:,}\n**Bots:** {bots:,}\n**En ligne:** {online:,}",
            inline=True
        )
        
        # Canaux
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📺 Canaux",
            value=f"**Texte:** {text_channels}\n**Vocal:** {voice_channels}\n**Catégories:** {categories}",
            inline=True
        )
        
        # Autres statistiques
        embed.add_field(
            name="🎭 Rôles",
            value=f"{len(guild.roles)}",
            inline=True
        )
        
        embed.add_field(
            name="😀 Emojis",
            value=f"{len(guild.emojis)}/{guild.emoji_limit}",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Boosts",
            value=f"Niveau {guild.premium_tier} ({guild.premium_subscription_count} boosts)",
            inline=True
        )
        
        # Fonctionnalités
        features = []
        if "COMMUNITY" in guild.features:
            features.append("🏘️ Communauté")
        if "PARTNERED" in guild.features:
            features.append("🤝 Partenaire")
        if "VERIFIED" in guild.features:
            features.append("✅ Vérifié")
        if "VANITY_URL" in guild.features:
            features.append("🔗 URL personnalisée")
        
        if features:
            embed.add_field(
                name="✨ Fonctionnalités",
                value="\n".join(features),
                inline=False
            )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Affiche l'avatar d'un membre")
    @app_commands.describe(member="Le membre dont afficher l'avatar")
    async def avatar(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Commande pour afficher l'avatar d'un membre"""
        
        target = member or interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ Avatar de {target.display_name}",
            color=target.color if target.color != discord.Color.default() else 0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=target.display_avatar.url)
        
        embed.add_field(
            name="🔗 Liens",
            value=f"[PNG]({target.display_avatar.with_format('png').url}) • "
                  f"[JPG]({target.display_avatar.with_format('jpg').url}) • "
                  f"[WEBP]({target.display_avatar.with_format('webp').url})",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Affiche la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        """Commande pour afficher la latence du bot"""
        
        # Mesure du temps de réponse
        start_time = datetime.utcnow()
        
        embed = discord.Embed(
            title="🏓 Pong !",
            description="Calcul de la latence...",
            color=0x7289da
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Calcul de la latence
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        # Mise à jour de l'embed
        embed.description = None
        embed.add_field(
            name="📡 Latence WebSocket",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Temps de réponse",
            value=f"{round(response_time)}ms",
            inline=True
        )
        
        # Couleur selon la latence
        avg_latency = (self.bot.latency * 1000 + response_time) / 2
        if avg_latency < 100:
            embed.color = 0x00ff00  # Vert
        elif avg_latency < 200:
            embed.color = 0xffff00  # Jaune
        else:
            embed.color = 0xff0000  # Rouge
        
        embed.timestamp = datetime.utcnow()
        
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="embed", description="Crée un message embed personnalisé")
    @app_commands.describe(
        title="Titre de l'embed",
        description="Description de l'embed",
        color="Couleur de l'embed (hex, ex: #ff0000)"
    )
    async def create_embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: Optional[str] = None,
        color: Optional[str] = None
    ):
        """Commande pour créer un embed personnalisé"""
        
        # Vérification des permissions
        if not interaction.user.guild_permissions.manage_messages:
            embed = EmbedBuilder.error(
                "Permission refusée",
                "Vous devez avoir la permission **Gérer les messages** pour utiliser cette commande."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Couleur par défaut
            embed_color = 0x7289da
            
            # Parsing de la couleur si fournie
            if color:
                if color.startswith('#'):
                    color = color[1:]
                try:
                    embed_color = int(color, 16)
                except ValueError:
                    embed_color = 0x7289da
            
            # Création de l'embed
            custom_embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color,
                timestamp=datetime.utcnow()
            )
            
            custom_embed.set_footer(
                text=f"Créé par {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.response.send_message(embed=custom_embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de créer l'embed: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(UtilitiesCog(bot))

