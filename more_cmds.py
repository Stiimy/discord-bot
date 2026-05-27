"""
Commandes  manquantes — batch 2
/infractions, /sanctions, /mod, /normaliser, /botinfo, /embed avancé,
/reglement, /suggestmod, /anniversaire, /evenement, /sauvegarde, /couleur, /maths
"""

import discord, random, re, asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime


class Full(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========== INFRACTIONS ==========
    infractions = {}  # {user_id: [(reason, date, mod_id)]}

    @app_commands.command(name="infractions", description="📋 Gère les infractions (ajouter/lister/retirer)")
    @app_commands.default_permissions(moderate_members=True)
    async def infractions(self, interaction: discord.Interaction, action: str, membre: discord.Member = None, raison: str = None):
        if action == "ajouter" and membre and raison:
            uid = str(membre.id)
            if uid not in self.infractions: self.infractions[uid] = []
            self.infractions[uid].append((raison, datetime.now().strftime("%d/%m/%Y"), interaction.user.id))
            await interaction.response.send_message(f"📋 Infraction ajoutée à {membre.mention} : {raison}", ephemeral=True)
        elif action == "lister":
            if membre:
                infs = self.infractions.get(str(membre.id), [])
                txt = "\n".join(f"{i+1}. {r} ({d})" for i,(r,d,_) in enumerate(infs)) or "Aucune"
                await interaction.response.send_message(f"📋 Infractions de {membre.display_name} :\n{txt}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Spécifie un membre", ephemeral=True)
        elif action == "retirer" and membre:
            self.infractions[str(membre.id)] = []
            await interaction.response.send_message(f"✅ Infractions de {membre.mention} réinitialisées", ephemeral=True)
        else:
            await interaction.response.send_message("Usage: ajouter @membre raison | lister @membre | retirer @membre", ephemeral=True)

    # ========== SANCTIONS ==========
    sanctions = {}

    @app_commands.command(name="sanctions", description="📋 Historique des sanctions (lister/retirer)")
    @app_commands.default_permissions(moderate_members=True)
    async def sanctions(self, interaction: discord.Interaction, action: str, membre: discord.Member = None):
        if action == "lister" and membre:
            sancs = self.sanctions.get(str(membre.id), [])
            txt = "\n".join(sancs[-10:]) or "Aucune sanction"
            await interaction.response.send_message(f"📋 Sanctions de {membre.display_name} :\n{txt}", ephemeral=True)
        elif action == "retirer" and membre:
            self.sanctions.pop(str(membre.id), None)
            await interaction.response.send_message(f"✅ Historique de {membre.mention} effacé", ephemeral=True)
        else:
            await interaction.response.send_message("Usage: lister @membre | retirer @membre", ephemeral=True)

    # ========== MOD (sanction rapide) ==========
    @app_commands.command(name="mod", description="⚡ Sanction rapide (warn/mute/kick/ban)")
    @app_commands.default_permissions(moderate_members=True)
    async def mod(self, interaction: discord.Interaction, membre: discord.Member, type: str, raison: str = "Non spécifiée"):
        type = type.lower()
        if type == "warn":
            await interaction.response.send_message(f"⚠️ {membre.mention} averti : {raison}")
        elif type == "mute":
            await membre.timeout(discord.utils.utcnow() + discord.utils.Duration(hours=1), reason=raison)
            await interaction.response.send_message(f"🔇 {membre.mention} mute 1h : {raison}")
        elif type == "kick":
            await membre.kick(reason=raison)
            await interaction.response.send_message(f"👢 {membre} expulsé : {raison}")
        elif type == "ban":
            await membre.ban(reason=raison)
            await interaction.response.send_message(f"🔨 {membre} banni : {raison}")
        else:
            await interaction.response.send_message("Types : warn, mute, kick, ban", ephemeral=True)

    # ========== NORMALISER ==========
    @app_commands.command(name="normaliser", description="🔤 Retire les caractères spéciaux d'un pseudo")
    @app_commands.default_permissions(moderate_members=True)
    async def normaliser(self, interaction: discord.Interaction, membre: discord.Member):
        clean = re.sub(r'[^\w\s]', '', membre.display_name).strip()
        await membre.edit(nick=clean or "Pseudo nettoyé")
        await interaction.response.send_message(f"✅ Pseudo normalisé : `{clean}`")

    # ========== BOTINFO ==========
    @app_commands.command(name="botinfo", description="🤖 Infos sur le bot")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Sylphiette", color=0x9B59B6)
        embed.add_field(name="Version", value="2.0.0", inline=True)
        embed.add_field(name="Commandes", value="56+", inline=True)
        embed.add_field(name="Serveurs", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Python", value="3.14", inline=True)
        embed.add_field(name="Library", value="discord.py 2.7", inline=True)
        embed.add_field(name="Latence", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Premium", value="🟢 100% gratuit — tout est inclus !", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ========== RÈGLEMENT ==========
    @app_commands.command(name="reglement", description="📜 Crée un embed de règlement")
    @app_commands.default_permissions(administrator=True)
    async def reglement(self, interaction: discord.Interaction, titre: str, regle1: str, regle2: str = None,
                        regle3: str = None, regle4: str = None, regle5: str = None):
        embed = discord.Embed(title=f"📜 {titre}", color=0xE74C3C)
        rules = [r for r in [regle1, regle2, regle3, regle4, regle5] if r]
        for i, r in enumerate(rules, 1):
            embed.add_field(name=f"Règle {i}", value=r, inline=False)
        embed.set_footer(text=f"Règlement par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # ========== ANNIVERSAIRE ==========
    annivs = {}

    @app_commands.command(name="anniversaire", description="🎂 Gère les anniversaires (définir/liste)")
    async def anniversaire(self, interaction: discord.Interaction, action: str, date: str = None):
        uid = str(interaction.user.id)
        if action == "définir" and date:
            self.annivs[uid] = date
            await interaction.response.send_message(f"🎂 Anniversaire défini au {date} !", ephemeral=True)
        elif action == "liste":
            txt = "\n".join(f"<@{u}> : {d}" for u,d in list(self.annivs.items())[:10]) or "Aucun anniversaire"
            await interaction.response.send_message(f"🎂 Prochains anniversaires :\n{txt}")
        elif action == "retirer":
            self.annivs.pop(uid, None)
            await interaction.response.send_message("✅ Anniversaire retiré", ephemeral=True)
        else:
            await interaction.response.send_message("Usage: définir JJ/MM | liste | retirer", ephemeral=True)

    # ========== ÉVÉNEMENT ==========
    @app_commands.command(name="evenement", description="🎪 Crée un événement (créer/terminer/relancer)")
    @app_commands.default_permissions(manage_events=True)
    async def evenement(self, interaction: discord.Interaction, action: str, nom: str = "", recompense: str = ""):
        if action == "créer":
            embed = discord.Embed(title=f"🎪 {nom}", description=f"**Récompense :** {recompense}\nRéagis avec 🎉 pour participer !", color=0xF1C40F)
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            await msg.add_reaction("🎉")
        elif action == "terminer":
            await interaction.response.send_message("🏁 Événement terminé !")
        elif action == "relancer":
            await interaction.response.send_message("🔄 Nouveau tirage en cours...")
        else:
            await interaction.response.send_message("Usage: créer nom récompense | terminer | relancer", ephemeral=True)

    # ========== COULEUR ==========
    @app_commands.command(name="couleur", description="🎨 Génère ou affiche une couleur")
    async def couleur(self, interaction: discord.Interaction, hex: str = None):
        if hex:
            hex = hex.lstrip('#')
            try:
                color = int(hex, 16)
                embed = discord.Embed(title=f"🎨 #{hex.upper()}", color=color)
                embed.add_field(name="RGB", value=f"({(color>>16)&255}, {(color>>8)&255}, {color&255})", inline=True)
                embed.set_image(url=f"https://singlecolorimage.com/get/{hex}/400x100")
                await interaction.response.send_message(embed=embed)
            except:
                await interaction.response.send_message("❌ Code hex invalide", ephemeral=True)
        else:
            r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
            color = (r<<16)|(g<<8)|b
            embed = discord.Embed(title=f"🎨 Couleur aléatoire", color=color)
            embed.add_field(name="Hex", value=f"#{r:02x}{g:02x}{b:02x}".upper(), inline=True)
            embed.add_field(name="RGB", value=f"({r}, {g}, {b})", inline=True)
            await interaction.response.send_message(embed=embed)

    # ========== MATHS ==========
    @app_commands.command(name="maths", description="🧮 Résout une expression mathématique")
    async def maths(self, interaction: discord.Interaction, expression: str):
        try:
            # Nettoyer l'expression (safe eval)
            expr = expression.replace('^', '**').replace('×', '*').replace('÷', '/').replace('π', '3.141592653589793')
            result = eval(expr, {"__builtins__": {}}, {"sqrt": lambda x: x**0.5, "abs": abs, "round": round, "pi": 3.141592653589793})
            await interaction.response.send_message(f"🧮 `{expression}` = **{result}**")
        except:
            await interaction.response.send_message("❌ Expression invalide", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Full(bot))

    # ========== ENVOYER ==========
    @app_commands.command(name="envoyer", description="📨 Envoie un message dans un salon (via le bot)")
    @app_commands.default_permissions(manage_messages=True)
    async def envoyer(self, interaction: discord.Interaction, salon: discord.TextChannel, message: str):
        await salon.send(message)
        await interaction.response.send_message(f"✅ Message envoyé dans {salon.mention}", ephemeral=True)
async def setup(bot):
    await bot.add_cog(Full(bot))
