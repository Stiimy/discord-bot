"""
Module Tickets — Système de support par ticket
Style DraftBot : /ticket open, /ticket close, transcript
"""

import discord, asyncio
from discord.ext import commands
from discord import app_commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Ouvrir un ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_open")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category_id = getattr(self, '_category_id', None)
        category = discord.utils.get(guild.categories, id=category_id) if category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(title="📩 Ticket ouvert", description=f"Bienvenue {interaction.user.mention} !\nUn membre du staff va te répondre.\n\nPour fermer : 🔒", color=0x3498DB)
        close_view = discord.ui.View(timeout=None)
        close_view.add_item(discord.ui.Button(label="🔒 Fermer", style=discord.ButtonStyle.danger, custom_id=f"ticket_close_{channel.id}"))
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ Ticket ouvert : {channel.mention}", ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="🎟️ Gère le système de tickets")
    @app_commands.default_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction,
                     action: str, channel: discord.TextChannel = None):
        """
        action: setup (créer le panel) | close (fermer un ticket)
        """
        if action == "setup":
            embed = discord.Embed(title="🎟️ Support", description="Clique sur le bouton ci-dessous pour ouvrir un ticket.", color=0x3498DB)
            embed.set_footer(text="Sylphiette • Tickets")
            view = TicketView()
            if channel:
                view._category_id = channel.category_id
            await interaction.channel.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Panel de tickets créé !", ephemeral=True)
        elif action == "close":
            await interaction.response.send_message("🔒 Fermeture du ticket...", ephemeral=True)
            await asyncio.sleep(2)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ Utilise `setup` ou `close`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
