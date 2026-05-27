"""
Module Logs — Journalisation complète du serveur
Style  : messages, joins, sanctions, vocaux

"""

import discord
from discord.ext import commands
from discord import app_commands
import os, json

DATA_FILE = "/home/stiimy/discord-bot/data/logs_config.json"

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self._load()

    def _load(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.config, f)

    def _get_channel(self, guild_id, key):
        cid = self.config.get(str(guild_id), {}).get(key)
        if not cid: return None
        return self.bot.get_channel(int(cid))

    def _enabled(self, guild_id, key):
        return self.config.get(str(guild_id), {}).get(key, False)

    async def _log(self, guild_id, key, embed):
        ch = self._get_channel(guild_id, key)
        if ch:
            try:
                await ch.send(embed=embed)
            except:
                pass

    @app_commands.command(name="logchannel", description="📜 Définit un salon de logs")
    @app_commands.default_permissions(administrator=True)
    async def logchannel(self, interaction: discord.Interaction,
                         type: str, channel: discord.TextChannel = None):
        """type: messages, joins, sanctions, vocaux. Sans channel = désactive"""
        guild_id = str(interaction.guild_id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        if channel:
            self.config[guild_id][type] = str(channel.id)
            await interaction.response.send_message(f"✅ Logs **{type}** → {channel.mention}", ephemeral=True)
        else:
            self.config[guild_id].pop(type, None)
            await interaction.response.send_message(f"🔴 Logs **{type}** désactivés", ephemeral=True)
        self._save()

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: return
        embed = discord.Embed(title="🗑️ Message supprimé", color=0xE74C3C, timestamp=discord.utils.utcnow())
        embed.add_field(name="Auteur", value=f"{message.author.mention} ({message.author.id})", inline=True)
        embed.add_field(name="Salon", value=message.channel.mention, inline=True)
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1024] or "*vide*", inline=False)
        await self._log(message.guild.id, "messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot: return
        if before.content == after.content: return
        embed = discord.Embed(title="✏️ Message modifié", color=0xF39C12, timestamp=discord.utils.utcnow())
        embed.add_field(name="Auteur", value=f"{before.author.mention}", inline=True)
        embed.add_field(name="Salon", value=before.channel.mention, inline=True)
        embed.add_field(name="Avant", value=before.content[:512] or "*vide*", inline=False)
        embed.add_field(name="Après", value=after.content[:512] or "*vide*", inline=False)
        await self._log(before.guild.id, "messages", embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title="👋 Membre rejoint", color=0x2ECC71, timestamp=discord.utils.utcnow())
        embed.add_field(name="Membre", value=f"{member.mention} ({member.id})", inline=True)
        embed.add_field(name="Compte créé", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await self._log(member.guild.id, "joins", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(title="🚪 Membre parti", color=0xE74C3C, timestamp=discord.utils.utcnow())
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await self._log(member.guild.id, "joins", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.guild: return
        if before.channel == after.channel: return
        embed = discord.Embed(timestamp=discord.utils.utcnow())
        if after.channel and not before.channel:
            embed.title = "🎤 Connecté en vocal"
            embed.description = f"{member.mention} → {after.channel.mention}"
            embed.color = 0x2ECC71
        elif before.channel and not after.channel:
            embed.title = "🔇 Déconnecté du vocal"
            embed.description = f"{member.mention} ← {before.channel.mention}"
            embed.color = 0x95A5A6
        else:
            embed.title = "🔄 Changement de salon vocal"
            embed.description = f"{member.mention} : {before.channel.mention} → {after.channel.mention}"
            embed.color = 0x3498DB
        await self._log(member.guild.id, "vocaux", embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))
