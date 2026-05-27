"""
Module Salons Vocaux Temporaires — Salons éphémères
Style 
"""

import discord
from discord.ext import commands
from discord import app_commands

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trigger_channels = {}  # channel_id -> category_id

    @app_commands.command(name="tempvoice", description="🎤 Configure les salons vocaux temporaires")
    @app_commands.default_permissions(administrator=True)
    async def tempvoice(self, interaction: discord.Interaction, 
                        trigger_channel: discord.VoiceChannel):
        self.trigger_channels[trigger_channel.id] = trigger_channel.category_id
        await interaction.response.send_message(
            f"✅ Salon vocal temporaire configuré : {trigger_channel.mention}\n"
            f"Quand un membre rejoint, un salon privé est créé.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id in self.trigger_channels:
            guild = member.guild
            category_id = self.trigger_channels[after.channel.id]
            category = discord.utils.get(guild.categories, id=category_id)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
            }

            channel = await guild.create_voice_channel(
                name=f"🔊 {member.display_name}",
                category=category,
                overwrites=overwrites
            )

            try:
                await member.move_to(channel)
            except:
                pass

            # Supprimer le salon quand il est vide
            while True:
                await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.Duration(seconds=5))
                if len(channel.members) == 0:
                    try:
                        await channel.delete()
                    except:
                        pass
                    break


async def setup(bot):
    await bot.add_cog(TempVoice(bot))
