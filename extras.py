"""
Module Rappels & Starboard
"""

import discord, asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remind", description="⏰ Crée un rappel")
    async def remind(self, interaction: discord.Interaction, duree: str, message: str):
        """duree: 30s, 5m, 1h, 1d"""
        import re
        match = re.match(r'(\d+)(s|m|h|d)', duree)
        if not match:
            await interaction.response.send_message("❌ Format : 30s, 5m, 1h, 1d", ephemeral=True)
            return
        val, unit = int(match.group(1)), match.group(2)
        seconds = val * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
        
        await interaction.response.send_message(f"⏰ Rappel dans {duree} : **{message}**", ephemeral=False)
        await asyncio.sleep(seconds)
        await interaction.channel.send(f"⏰ {interaction.user.mention} — Rappel : **{message}**")

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_channel = None
        self.min_stars = 3

    @app_commands.command(name="starboard", description="⭐ Configure le starboard")
    @app_commands.default_permissions(administrator=True)
    async def starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, min_stars: int = 3):
        self.starboard_channel = channel
        self.min_stars = min_stars
        await interaction.response.send_message(f"✅ Starboard → {channel.mention} (min {min_stars} ⭐)", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not self.starboard_channel: return
        if str(payload.emoji) != "⭐": return
        if payload.user_id == self.bot.user.id: return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel: return
        try:
            msg = await channel.fetch_message(payload.message_id)
            stars = sum(1 for r in msg.reactions if str(r.emoji) == "⭐")
            if stars >= self.min_stars:
                embed = discord.Embed(description=msg.content or "*[média]*", color=0xF1C40F, timestamp=msg.created_at)
                embed.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
                embed.add_field(name="Message original", value=f"[Aller au message]({msg.jump_url})", inline=False)
                embed.set_footer(text=f"⭐ {stars}")
                await self.starboard_channel.send(embed=embed)
        except:
            pass

async def setup(bot):
    await bot.add_cog(Reminders(bot))
    await bot.add_cog(Starboard(bot))
