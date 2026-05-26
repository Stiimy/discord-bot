"""
Module Auto-Modération — Protection anti-spam, anti-lien, anti-raid, anti-mass mention
Style DraftBot — toute la config est gratuite
Inspiré de : draftbot.fr/docs/modules/auto-moderation
"""

import discord, re, asyncio
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
from datetime import datetime, timedelta

# Seuils par défaut
DEFAULTS = {
    "spam_threshold": 5,       # messages identiques
    "spam_window": 5,          # secondes
    "caps_ratio": 0.7,         # 70% de majuscules
    "caps_min_length": 10,     # longueur min du message
    "mention_limit": 5,        # max mentions par message
    "raid_joins": 10,          # joins en X secondes
    "raid_window": 30,         # secondes
}

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_cache = defaultdict(list)  # user_id -> [(timestamp, content)]
        self.join_cache = []                 # [(timestamp, member)]
        self.ignored_roles = set()
        self.ignored_channels = set()
        self.allowed_domains = {"discord.gg", "discord.com", "tenor.com", "giphy.com", "imgur.com", "youtube.com", "youtu.be", "twitch.tv", "spotify.com"}

    # ============================================================
    # ÉVÉNEMENTS
    # ============================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        if not message.guild: return
        if any(r.id in self.ignored_roles for r in message.author.roles): return
        if message.channel.id in self.ignored_channels: return

        await self._check_spam(message)
        await self._check_caps(message)
        await self._check_links(message)
        await self._check_mentions(message)

    async def _check_spam(self, message):
        now = datetime.now()
        uid = message.author.id
        content = message.content

        # Nettoyer le cache des entrées expirées
        self.spam_cache[uid] = [
            (t, c) for t, c in self.spam_cache[uid]
            if (now - t).total_seconds() < DEFAULTS["spam_window"]
        ]
        self.spam_cache[uid].append((now, content))

        # Vérifier les doublons
        duplicates = [c for t, c in self.spam_cache[uid] if c == content and c]
        if len(duplicates) >= DEFAULTS["spam_threshold"]:
            try:
                await message.delete()
                await message.channel.send(
                    f"🛡️ {message.author.mention} — **Anti-spam** : message supprimé (x{len(duplicates)} doublons)",
                    delete_after=5
                )
            except:
                pass

    async def _check_caps(self, message):
        content = message.content
        if len(content) < DEFAULTS["caps_min_length"]: return
        if not content.isascii(): return  # ignore non-ASCII (emojis, accents)

        caps = sum(1 for c in content if c.isupper() and c.isalpha())
        total = sum(1 for c in content if c.isalpha())
        if total == 0: return

        if caps / total >= DEFAULTS["caps_ratio"]:
            try:
                await message.delete()
                await message.channel.send(
                    f"🛡️ {message.author.mention} — **Anti-majuscules** : évite les messages en MAJUSCULES",
                    delete_after=5
                )
            except:
                pass

    async def _check_links(self, message):
        urls = re.findall(r'(https?://\S+)', message.content)
        if not urls: return

        for url in urls:
            domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            if domain not in self.allowed_domains:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"🛡️ {message.author.mention} — **Anti-lien** : `{domain}` n'est pas autorisé",
                        delete_after=5
                    )
                except:
                    pass
                return

    async def _check_mentions(self, message):
        mentions = len(message.mentions) + len(message.role_mentions)
        if mentions >= DEFAULTS["mention_limit"]:
            try:
                await message.delete()
                await message.channel.send(
                    f"🛡️ {message.author.mention} — **Anti-mention** : max {DEFAULTS['mention_limit']} mentions par message",
                    delete_after=5
                )
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        now = datetime.now()
        self.join_cache.append((now, member))
        # Nettoyer
        self.join_cache = [(t, m) for t, m in self.join_cache if (now - t).total_seconds() < DEFAULTS["raid_window"]]

        if len(self.join_cache) >= DEFAULTS["raid_joins"]:
            # Raid détecté
            for _, m in self.join_cache:
                try:
                    await m.kick(reason="Anti-raid : trop de joins rapides")
                except:
                    pass
            self.join_cache.clear()

    # ============================================================
    # COMMANDES SLASH
    # ============================================================

    @app_commands.command(name="antispam", description="🛡️ Configure les seuils anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def antispam(self, interaction: discord.Interaction,
                       seuil: int = 5, fenetre: int = 5):
        DEFAULTS["spam_threshold"] = seuil
        DEFAULTS["spam_window"] = fenetre
        await interaction.response.send_message(
            f"✅ Anti-spam : {seuil} messages identiques en {fenetre}s → suppression", ephemeral=True)

    @app_commands.command(name="antilien", description="🔗 Autorise ou bloque un domaine")
    @app_commands.default_permissions(administrator=True)
    async def antilien(self, interaction: discord.Interaction, domaine: str, action: str):
        """Autorise ou bloque un domaine. action = allow | block"""
        if action == "allow":
            self.allowed_domains.add(domaine)
            await interaction.response.send_message(f"✅ `{domaine}` autorisé", ephemeral=True)
        elif action == "block":
            self.allowed_domains.discard(domaine)
            await interaction.response.send_message(f"🔴 `{domaine}` bloqué", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Utilise `allow` ou `block`", ephemeral=True)

    @app_commands.command(name="ignore", description="🚫 Ignore un rôle ou salon pour l'auto-mod")
    @app_commands.default_permissions(administrator=True)
    async def ignore(self, interaction: discord.Interaction,
                     role: discord.Role = None, channel: discord.TextChannel = None):
        if role:
            self.ignored_roles.add(role.id)
            await interaction.response.send_message(f"✅ Le rôle {role.mention} est ignoré par l'auto-mod", ephemeral=True)
        elif channel:
            self.ignored_channels.add(channel.id)
            await interaction.response.send_message(f"✅ Le salon {channel.mention} est ignoré par l'auto-mod", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Spécifie un rôle ou un salon", ephemeral=True)

    @app_commands.command(name="raidmode", description="🛡️ Active/désactive le mode raid")
    @app_commands.default_permissions(administrator=True)
    async def raidmode(self, interaction: discord.Interaction, active: bool):
        DEFAULTS["raid_joins"] = 5 if active else 999
        await interaction.response.send_message(
            f"{'🟢 Mode raid ACTIVÉ' if active else '🔴 Mode raid DÉSACTIVÉ'}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
