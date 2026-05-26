"""
Module Rôles-Réactions — Auto-rôle via réaction Discord
Style DraftBot : /reactionrole add <message_id> <emoji> <role>
Inspiré de : draftbot.fr/docs/modules/roles-reactions
"""

import discord
from discord.ext import commands
from discord import app_commands
import json, os

DATA_FILE = "/home/stiimy/discord-bot/data/reaction_roles.json"

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self._load()

    def _load(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id: return
        key = f"{payload.message_id}:{payload.emoji.name}"
        role_id = self.data.get(key)
        if not role_id: return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild: return
        role = guild.get_role(int(role_id))
        if not role: return

        member = guild.get_member(payload.user_id)
        if not member: return

        try:
            await member.add_roles(role)
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id: return
        key = f"{payload.message_id}:{payload.emoji.name}"
        role_id = self.data.get(key)
        if not role_id: return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild: return
        role = guild.get_role(int(role_id))
        if not role: return

        member = guild.get_member(payload.user_id)
        if not member: return

        try:
            await member.remove_roles(role)
        except:
            pass

    @app_commands.command(name="reactionrole", description="🎯 Ajoute un rôle-réaction sur un message")
    @app_commands.default_permissions(administrator=True)
    async def reactionrole(self, interaction: discord.Interaction,
                           message_id: str, emoji: str, role: discord.Role):
        try:
            msg_id = int(message_id)
        except:
            await interaction.response.send_message("❌ ID de message invalide", ephemeral=True)
            return

        channel = interaction.channel
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.add_reaction(emoji)
        except:
            await interaction.response.send_message("❌ Message introuvable ou emoji invalide", ephemeral=True)
            return

        key = f"{msg_id}:{emoji}"
        self.data[key] = str(role.id)
        self._save()

        await interaction.response.send_message(
            f"✅ Rôle-réaction ajouté : {emoji} → {role.mention}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
