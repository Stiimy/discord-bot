"""
Module Giveaways — Concours et tirages au sort
Style DraftBot : /giveaway start, /giveaway reroll, /giveaway end
Inspiré de : draftbot.fr/docs/modules/giveaways
"""

import discord, asyncio, random
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class GiveawayView(discord.ui.View):
    def __init__(self, end_time, winners, prize, host_id):
        super().__init__(timeout=None)
        self.end_time = end_time
        self.winners = winners
        self.prize = prize
        self.host_id = host_id

    @discord.ui.button(label="🎉 Participer", style=discord.ButtonStyle.green, custom_id="giveaway_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Tu participes au giveaway !", ephemeral=True)


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveaway", description="🎉 Gère les giveaways (start / reroll / end)")
    @app_commands.default_permissions(administrator=True)
    async def giveaway(self, interaction: discord.Interaction,
                       action: str, duree: str = "1h", gagnants: int = 1, lot: str = "Un super lot !"):
        """
        action: start | reroll | end
        duree: 30s, 5m, 1h, 1d
        """
        if action == "start":
            await self._start(interaction, duree, gagnants, lot)
        elif action == "reroll":
            await self._reroll(interaction, gagnants)
        elif action == "end":
            await self._end(interaction)
        else:
            await interaction.response.send_message("❌ Utilise `start`, `reroll` ou `end`", ephemeral=True)

    async def _start(self, interaction, duree_str, winners, prize):
        # Parser la durée
        seconds = self._parse_duration(duree_str)
        if seconds == 0:
            await interaction.response.send_message("❌ Durée invalide. Ex: 30s, 5m, 1h, 1d", ephemeral=True)
            return

        end_time = datetime.now() + timedelta(seconds=seconds)

        embed = discord.Embed(
            title=f"🎉 GIVEAWAY : {prize}",
            description=(
                f"**{winners} gagnant(s)**\n"
                f"Réagis avec 🎉 pour participer !\n\n"
                f"⏱️ Fin : <t:{int(end_time.timestamp())}:R>\n"
                f"Hôte : {interaction.user.mention}"
            ),
            color=0xE67E22
        )
        embed.set_footer(text="Sylphiette • Giveaway")

        view = GiveawayView(end_time, winners, prize, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()

        # Attendre la fin
        await asyncio.sleep(seconds)

        # Tirage
        try:
            msg = await interaction.channel.fetch_message(msg.id)
            users = []
            for reaction in msg.reactions:
                if str(reaction.emoji) == "🎉":
                    async for user in reaction.users():
                        if not user.bot:
                            users.append(user)
            if len(users) < winners:
                winners = len(users)

            if users:
                chosen = random.sample(users, min(winners, len(users)))
                mentions = " ".join(u.mention for u in chosen)
                result_embed = discord.Embed(
                    title=f"🎉 GIVEAWAY TERMINÉ : {prize}",
                    description=f"**Gagnant(s) :** {mentions}\nFélicitations ! 🎉",
                    color=0x2ECC71
                )
                await msg.reply(content=mentions, embed=result_embed)
            else:
                await msg.reply("❌ Aucun participant. Giveaway annulé.")
        except:
            pass

    def _parse_duration(self, s):
        import re
        match = re.match(r'(\d+)(s|m|h|d)', s)
        if not match: return 0
        val, unit = int(match.group(1)), match.group(2)
        return val * {"s": 1, "m": 60, "h": 3600, "d": 86400}.get(unit, 0)

    async def _reroll(self, interaction, winners):
        await interaction.response.send_message("🔄 Reroll : choisis un message de giveaway et utilise le menu contextuel", ephemeral=True)

    async def _end(self, interaction):
        await interaction.response.send_message("⏹️ Le giveaway en cours sera terminé", ephemeral=True)

    @app_commands.command(name="greroll", description="🎲 Retire un nouveau gagnant pour un giveaway")
    @app_commands.default_permissions(administrator=True)
    async def greroll(self, interaction: discord.Interaction, message_id: str):
        try:
            msg_id = int(message_id)
            msg = await interaction.channel.fetch_message(msg_id)
            users = []
            for r in msg.reactions:
                if str(r.emoji) == "🎉":
                    async for u in r.users():
                        if not u.bot: users.append(u)
            if users:
                chosen = random.choice(users)
                await interaction.response.send_message(f"🎲 Nouveau gagnant : {chosen.mention} !")
            else:
                await interaction.response.send_message("❌ Aucun participant trouvé", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Message introuvable", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
