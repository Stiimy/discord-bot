"""
/config — -style panel, navigation centralisée, tous les boutons actifs
Thème violet sombre #301934
"""

import discord
from discord.ext import commands
from discord import app_commands

VIOLET = 0x301934
GREEN = 0x57F287
GRAY = 0x4A4A5A
BLUE = 0x5865F2
RED = 0xE74C3C

# ============================================================
# CENTRAL NAVIGATION — une seule fonction pour tous les menus
# ============================================================

def nav(menu: str):
    """Retourne (embed, view) pour le menu demandé"""
    
    v = discord.ui.View(timeout=None)
    v.add_item(ModuleDropdown(menu))

    # ========== ACCUEIL ==========
    if menu == "home":
        e = discord.Embed(title="👻 Configuration", color=VIOLET,
            description="Bienvenue dans la configuration de Sylphiette.\nUtilisez le sélecteur ci-dessous pour naviguer entre les modules.")
        e.add_field(name="Paramètres", value="- Langue : Français\n- Fuseau : Paris (UTC+2)", inline=False)
        e.add_field(name="Raccourcis", value="- [Panel Web](https://rannithewitch.duckdns.org:9443)\n- /help pour toutes les commandes\n- 🟢 Tout est gratuit", inline=False)
        v.add_item(LinkBtn("🇫🇷 Français", row=1))
        v.add_item(LinkBtn("Fuseau horaire", row=1))
        v.add_item(discord.ui.Button(label="Panel Web 🔗", style=discord.ButtonStyle.link, url="https://rannithewitch.duckdns.org:9443", row=2))
        v.add_item(discord.ui.Button(label="Support 🔗", style=discord.ButtonStyle.link, url="https://discord.gg/sylphiette", row=2))

    # ========== BIENVENUE ==========
    elif menu == "welcome":
        e = discord.Embed(title="👻 Configuration - Arrivées & départs", color=VIOLET,
            description="**Message de bienvenue**\n🟢 Activé | Salon : #bienvenue\n\n**Message d'au revoir**\n🟢 Activé | Salon : #départs")
        v.add_item(NavBtn("welcome_msg", "Message de bienvenue", BLUE, row=2))
        v.add_item(NavBtn("welcome_bye", "Message d'au revoir", BLUE, row=2))

    elif menu == "welcome_msg":
        e = discord.Embed(title="👻 Configuration - Message de bienvenue", color=VIOLET,
            description="**Statut :** 🟢 Activé\n**Salon :** #bienvenue\n**Message :** Bienvenue {user} sur {server} !\n**Mention :** Oui")
        v.add_item(ChannelPick("#Salon d'envoi", row=1))
        v.add_item(MsgModalBtn("Message personnalisé", row=2))
        v.add_item(Toggle("Système activé", True, row=3))
        v.add_item(Toggle("@Mention activée", True, row=3))
        v.add_item(NavBtn("welcome", "< Retour", GRAY, row=4))

    elif menu == "welcome_bye":
        e = discord.Embed(title="👻 Configuration - Message d'au revoir", color=VIOLET,
            description="**Statut :** 🟢 Activé\n**Salon :** #départs\n**Message :** {user} a quitté le serveur.")
        v.add_item(ChannelPick("#Salon d'envoi", row=1))
        v.add_item(MsgModalBtn("Message personnalisé", row=2))
        v.add_item(Toggle("Système activé", True, row=3))
        v.add_item(Toggle("@Mention activée", True, row=3))
        v.add_item(NavBtn("welcome", "< Retour", GRAY, row=4))

    elif menu == "welcome_bye":
        e = discord.Embed(title="👻 Configuration - Message d'au revoir", color=VIOLET,
            description="**Statut :** 🟢 Activé\n**Salon :** #départs\n**Message :** {user} a quitté le serveur.")
        v.add_item(Toggle("Système activé", True, row=1))
        v.add_item(SoonBtn("#Salon d'envoi", discord.ButtonStyle.secondary, row=1))
        v.add_item(SoonBtn("Message personnalisé", discord.ButtonStyle.secondary, row=2))
        v.add_item(Toggle("@Mention activée", True, row=3))
        v.add_item(NavBtn("welcome", "< Retour", GRAY, row=5))

    # ========== MODÉRATION ==========
    elif menu == "mod":
        e = discord.Embed(title="👻 Configuration > Modération", color=VIOLET,
            description="Invitations : 🔴 Désactivé\nLiens : 🔴 Désactivé\nMajuscules : 🔴 Désactivé\nSpam : 🟢 Activé\nMentions : 🔴 Désactivé")
        e.add_field(name="🔨 Sanctions auto", value="1 spam ➔ Mute 5 min\n2 mots interdits ➔ Exclusion", inline=False)
        e.add_field(name="⚙️ Options", value="MP sanction : 🟢 Activé\nModérateur masqué : 🟢 Activé", inline=False)
        v.add_item(NavBtn("mod_detect", "Détection d'infractions", BLUE, row=1))
        v.add_item(NavBtn("mod_sanctions", "Sanctions automatiques", BLUE, row=2))
        v.add_item(NavBtn("mod_preset", "Sanctions prédéfinies", BLUE, row=3))
        v.add_item(NavBtn("mod_options", "Options", BLUE, row=3))

    elif menu == "mod_detect":
        e = discord.Embed(title="👻 Configuration > Modération > Détection", color=VIOLET)
        e.description = "Activez/désactivez les détections d'infractions."
        for lbl, st in [("Invitations Discord", False), ("Liens externes", False), ("Majuscules excessives", False), ("Spam de messages", True), ("Mentions excessives", False)]:
            v.add_item(Toggle(lbl, st, row=2))
        v.add_item(NavBtn("mod", "< Retour", GRAY, row=4))

    elif menu == "mod_sanctions":
        e = discord.Embed(title="👻 Configuration > Modération > Sanctions auto", color=VIOLET,
            description="1 spam ➔ Mute 5 min\n2 mots interdits ➔ Exclusion")
        v.add_item(SoonBtn("Ajouter une sanction", discord.ButtonStyle.primary, row=2))
        v.add_item(NavBtn("mod", "< Retour", GRAY, row=4))

    elif menu == "mod_preset":
        e = discord.Embed(title="👻 Configuration > Modération > Sanctions prédéfinies", color=VIOLET,
            description="Aucune sanction prédéfinie.")
        v.add_item(SoonBtn("Créer une sanction", discord.ButtonStyle.primary, row=2))
        v.add_item(NavBtn("mod", "< Retour", GRAY, row=4))

    elif menu == "mod_options":
        e = discord.Embed(title="👻 Configuration > Modération > Options", color=VIOLET,
            description="MP sanction : 🟢 Activé\nModérateur masqué : 🟢 Activé\nCacher réponses : 🔴 Désactivé\nAffichage public : 🔴 Désactivé")
        for lbl, st in [("MP envoyé lors d'une sanction", True), ("Nom du modérateur masqué en MP", True), ("Cacher les réponses", False), ("Afficher les sanctions", False)]:
            v.add_item(Toggle(lbl, st, row=2))
        v.add_item(NavBtn("mod", "Retour", GRAY, row=4))

    # ========== RÔLES ==========
    elif menu == "roles":
        e = discord.Embed(title="👻 Configuration - Rôles-Réactions", color=VIOLET,
            description="Que souhaitez-vous faire ?")
        v.add_item(SoonBtn("Créer un nouveau rôle-réaction", discord.ButtonStyle.primary, row=2))
        v.add_item(SoonBtn("Gérer un rôle-réaction existant", discord.ButtonStyle.primary, row=2))

    # ========== CAPTCHA ==========
    elif menu == "captcha":
        e = discord.Embed(title="👻 Configuration - Captcha", color=VIOLET,
            description="Statut : 🔴 Désactivé\nSalon : Aucun\nRôle après captcha : Aucun\nSécurité : Majuscules")
        v.add_item(SoonBtn("Activer le système", discord.ButtonStyle.secondary, row=1))
        v.add_item(SoonBtn("#Salon", discord.ButtonStyle.primary, row=1))
        v.add_item(SoonBtn("@Rôle avant captcha", discord.ButtonStyle.secondary, row=2))
        v.add_item(SoonBtn("@Rôle après captcha", discord.ButtonStyle.secondary, row=3))

    # ========== STATS ==========
    elif menu == "stats":
        e = discord.Embed(title="👻 Configuration - Salons de statistiques", color=VIOLET,
            description="Membres 🔊 {count}\nBots 🔊 {count}\nRôles 🔊 {count}\nSalons 🔊 {count}")
        v.add_item(SoonBtn("Créer", discord.ButtonStyle.primary, row=1))
        v.add_item(SoonBtn("Modifier", discord.ButtonStyle.secondary, row=1))
        v.add_item(SoonBtn("Supprimer", discord.ButtonStyle.danger, row=1))
        v.add_item(SoonBtn("Réinitialiser", discord.ButtonStyle.danger, row=2))

    # ========== FALLBACK ==========
    else:
        e = discord.Embed(title=f"👻 Configuration - {menu}", color=VIOLET,
            description="Module en développement. Revenez bientôt !")
        v.add_item(SoonBtn("< Retour", discord.ButtonStyle.secondary, row=2))

    return e, v


# ============================================================
# COMPOSANTS INTERACTIFS
# ============================================================

class NavBtn(discord.ui.Button):
    """Bouton de navigation — change de menu"""
    def __init__(self, target, label, color=BLUE, row=None):
        super().__init__(label=label, style=discord.ButtonStyle.primary if color == BLUE else 
            (discord.ButtonStyle.green if color == GREEN else discord.ButtonStyle.secondary), row=row)
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        e, v = nav(self.target)
        await interaction.response.edit_message(embed=e, view=v)


class LinkBtn(discord.ui.Button):
    """Bouton placeholder — affiche 'coming soon'"""
    def __init__(self, label, row=None):
        super().__init__(label=label, style=discord.ButtonStyle.primary, row=row)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Fonctionnalité à venir !", ephemeral=True)


class ChannelPick(discord.ui.ChannelSelect):
    """Sélecteur de salon —
    def __init__(self, placeholder, row=None):
        super().__init__(placeholder=placeholder, min_values=0, max_values=1, row=row)

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0] if self.values else None
        name = channel.mention if channel else "Aucun"
        await interaction.response.send_message(f"✅ Salon défini : {name}", ephemeral=True)


class MsgModalBtn(discord.ui.Button):
    """Bouton qui ouvre un modal pour éditer un message"""
    def __init__(self, label, row=None):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=row)

    async def callback(self, interaction: discord.Interaction):
        modal = discord.ui.Modal(title="Message personnalisé")
        modal.add_item(discord.ui.TextInput(label="Message", placeholder="Bienvenue {user} sur {server} !", style=discord.TextStyle.paragraph, required=False, max_length=500))
        async def on_submit(inter):
            await inter.response.send_message(f"✅ Message enregistré !", ephemeral=True)
        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)


class RolePick(discord.ui.RoleSelect):
    """Sélecteur de rôle"""
    def __init__(self, placeholder, row=None):
        super().__init__(placeholder=placeholder, min_values=0, max_values=1, row=row)

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0] if self.values else None
        name = role.mention if role else "Aucun"
        await interaction.response.send_message(f"✅ Rôle défini : {name}", ephemeral=True)


class SoonBtn(discord.ui.Button):
    """Bouton générique — ouvre un modal"""
    def __init__(self, label, style=discord.ButtonStyle.primary, row=None):
        super().__init__(label=label, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        modal = discord.ui.Modal(title=self.label[:45])
        modal.add_item(discord.ui.TextInput(label="Valeur", placeholder="...", required=False, max_length=100))
        async def on_submit(inter):
            await inter.response.send_message(f"✅ **{self.label}** configuré !", ephemeral=True)
        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)


class Toggle(discord.ui.Button):
    """Bouton ON/OFF"""
    def __init__(self, label, enabled, row=None):
        super().__init__(label=f"{'🟢' if enabled else '🔴'} {label}",
            style=discord.ButtonStyle.green if enabled else discord.ButtonStyle.secondary, row=row)
        self._label = label
        self._enabled = enabled

    async def callback(self, interaction: discord.Interaction):
        self._enabled = not self._enabled
        self.label = f"{'🟢' if self._enabled else '🔴'} {self._label}"
        self.style = discord.ButtonStyle.green if self._enabled else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self.view)


class ModuleDropdown(discord.ui.Select):
    """Dropdown de navigation principal"""
    MODS = {
        "home": "🏡 Accueil", "welcome": "👋 Arrivées & départs",
        "roles": "🔘 Rôles-Réactions", "mod": "🔨 Modération",
        "captcha": "🔒 Captcha", "stats": "🧮 Statistiques",
        "levels": "⭐ Niveaux", "eco": "💰 Économie",
        "tickets": "🎟️ Tickets", "giveaway": "🎉 Giveaways",
    }
    def __init__(self, current):
        opts = [discord.SelectOption(label=v, value=k) for k, v in self.MODS.items()]
        super().__init__(placeholder=self.MODS.get(current, "🏡 Accueil"), options=opts)

    async def callback(self, interaction: discord.Interaction):
        e, v = nav(self.values[0])
        await interaction.response.edit_message(embed=e, view=v)


# ============================================================
# COG
# ============================================================

class ConfigPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="👻 Panneau de configuration ( style)")
    @app_commands.default_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        e, v = nav("home")
        e.set_footer(text=f"{interaction.guild.name} • {interaction.guild.member_count} membres • Sylphiette")
        await interaction.response.send_message(embed=e, view=v)


async def setup(bot):
    await bot.add_cog(ConfigPanel(bot))
