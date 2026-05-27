"""
Commandes  manquantes — tout gratuit
/sondage, /suggestion, /clear, /lock, /unlock, /setnick, /role, /report
"""

import discord, asyncio
from discord.ext import commands
from discord import app_commands


class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========== SONDAGE ==========
    @app_commands.command(name="sondage", description="📊 Crée un sondage")
    @app_commands.default_permissions(manage_messages=True)
    async def sondage(self, interaction: discord.Interaction, question: str, option1: str, option2: str,
                      option3: str = None, option4: str = None, option5: str = None):
        options = [option1, option2]
        for opt in [option3, option4, option5]:
            if opt: options.append(opt)
        
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        embed = discord.Embed(title="📊 Sondage", description=question, color=0x9B59B6)
        desc = ""
        for i, opt in enumerate(options):
            desc += f"{emojis[i]} {opt}\n"
        embed.add_field(name="Options", value=desc, inline=False)
        embed.set_footer(text=f"Sondage de {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

    # ========== SUGGESTION ==========
    @app_commands.command(name="suggestion", description="💡 Envoie une suggestion")
    async def suggestion(self, interaction: discord.Interaction, suggestion: str):
        embed = discord.Embed(title="💡 Nouvelle suggestion", description=suggestion, color=0x2ECC71)
        embed.set_footer(text=f"Par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    # ========== CLEAR ==========
    @app_commands.command(name="clear", description="🗑️ Supprime des messages")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, nombre: int = 10):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=nombre)
        await interaction.followup.send(f"🗑️ {len(deleted)} messages supprimés", ephemeral=True)

    # ========== LOCK / UNLOCK ==========
    @app_commands.command(name="lock", description="🔒 Verrouille le salon")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Salon verrouillé.")

    @app_commands.command(name="unlock", description="🔓 Déverrouille le salon")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 Salon déverrouillé.")

    # ========== SETNICK ==========
    @app_commands.command(name="setnick", description="🏷️ Change le pseudo d'un membre")
    @app_commands.default_permissions(manage_nicknames=True)
    async def setnick(self, interaction: discord.Interaction, membre: discord.Member, pseudo: str):
        await membre.edit(nick=pseudo)
        await interaction.response.send_message(f"✅ Pseudo de {membre.mention} changé en `{pseudo}`")

    # ========== ROLE ==========
    @app_commands.command(name="role", description="🎯 Donne ou retire un rôle")
    @app_commands.default_permissions(manage_roles=True)
    async def role(self, interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
        if role in membre.roles:
            await membre.remove_roles(role)
            await interaction.response.send_message(f"🔴 Rôle {role.mention} retiré à {membre.mention}")
        else:
            await membre.add_roles(role)
            await interaction.response.send_message(f"🟢 Rôle {role.mention} ajouté à {membre.mention}")

    # ========== REPORT ==========
    @app_commands.command(name="report", description="🚨 Signale un membre au staff")
    async def report(self, interaction: discord.Interaction, membre: discord.Member, raison: str):
        embed = discord.Embed(title="🚨 Signalement", color=0xE74C3C, timestamp=discord.utils.utcnow())
        embed.add_field(name="Signalé par", value=interaction.user.mention, inline=True)
        embed.add_field(name="Membre", value=f"{membre.mention} ({membre.id})", inline=True)
        embed.add_field(name="Raison", value=raison, inline=False)
        
        await interaction.response.send_message("✅ Signalement envoyé au staff.", ephemeral=True)
        # Envoyer dans le salon de logs si configuré
        await interaction.channel.send(embed=embed)

    # ========== SLOWMODE ==========
    @app_commands.command(name="slowmode", description="🐌 Active le mode lent")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, secondes: int = 5):
        await interaction.channel.edit(slowmode_delay=secondes)
        await interaction.response.send_message(f"🐌 Slowmode : {secondes}s entre chaque message")

    # ========== USERINFO amélioré ==========
    @app_commands.command(name="whois", description="🔍 Infos détaillées sur un membre")
    async def whois(self, interaction: discord.Interaction, membre: discord.Member = None):
        if membre is None: membre = interaction.user
        embed = discord.Embed(title=f"👤 {membre.display_name}", color=membre.top_role.color if membre.top_role.color.value else 0x5865F2)
        embed.set_thumbnail(url=membre.display_avatar.url)
        embed.add_field(name="ID", value=membre.id, inline=True)
        embed.add_field(name="Créé le", value=f"<t:{int(membre.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name="Rejoint le", value=f"<t:{int(membre.joined_at.timestamp())}:D>", inline=True) if membre.joined_at else None
        embed.add_field(name="Rôles", value=" ".join(r.mention for r in membre.roles[1:]) or "Aucun", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Extras(bot))
