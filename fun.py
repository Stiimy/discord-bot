"""
Module de commandes amusantes pour Smiity Bot
Commandes de divertissement et jeux
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime
import random
import asyncio

from utils.embeds import EmbedBuilder

class FunCog(commands.Cog):
    """Cog pour les commandes amusantes"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="8ball", description="Pose une question à la boule magique")
    @app_commands.describe(question="La question à poser")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Commande boule magique 8ball"""
        
        responses = [
            "🎱 C'est certain.",
            "🎱 Sans aucun doute.",
            "🎱 Oui, définitivement.",
            "🎱 Vous pouvez compter dessus.",
            "🎱 Comme je le vois, oui.",
            "🎱 Très probablement.",
            "🎱 Les perspectives sont bonnes.",
            "🎱 Oui.",
            "🎱 Les signes pointent vers oui.",
            "🎱 Réponse floue, essayez à nouveau.",
            "🎱 Demandez à nouveau plus tard.",
            "🎱 Mieux vaut ne pas vous le dire maintenant.",
            "🎱 Impossible de prédire maintenant.",
            "🎱 Concentrez-vous et demandez à nouveau.",
            "🎱 N'y comptez pas.",
            "🎱 Ma réponse est non.",
            "🎱 Mes sources disent non.",
            "🎱 Les perspectives ne sont pas si bonnes.",
            "🎱 Très douteux."
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Boule Magique",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="❓ Question",
            value=question,
            inline=False
        )
        
        embed.add_field(
            name="💭 Réponse",
            value=response,
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="Lance un ou plusieurs dés")
    @app_commands.describe(
        sides="Nombre de faces du dé (défaut: 6)",
        count="Nombre de dés à lancer (défaut: 1)"
    )
    async def dice(self, interaction: discord.Interaction, sides: Optional[int] = 6, count: Optional[int] = 1):
        """Commande pour lancer des dés"""
        
        if sides < 2 or sides > 100:
            embed = EmbedBuilder.error(
                "Nombre de faces invalide",
                "Le nombre de faces doit être entre 2 et 100."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if count < 1 or count > 10:
            embed = EmbedBuilder.error(
                "Nombre de dés invalide",
                "Vous pouvez lancer entre 1 et 10 dés."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Lancement des dés
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        
        embed = discord.Embed(
            title="🎲 Lancement de dés",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        if count == 1:
            embed.add_field(
                name=f"🎲 Dé à {sides} faces",
                value=f"**Résultat:** {results[0]}",
                inline=False
            )
        else:
            dice_emoji = "🎲" * min(count, 5)
            results_text = " + ".join(map(str, results))
            
            embed.add_field(
                name=f"{dice_emoji} {count} dés à {sides} faces",
                value=f"**Résultats:** {results_text}\n**Total:** {total}",
                inline=False
            )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="choose", description="Choisit aléatoirement entre plusieurs options")
    @app_commands.describe(options="Options séparées par des virgules")
    async def choose(self, interaction: discord.Interaction, options: str):
        """Commande pour choisir entre plusieurs options"""
        
        # Séparation des options
        choices = [choice.strip() for choice in options.split(',') if choice.strip()]
        
        if len(choices) < 2:
            embed = EmbedBuilder.error(
                "Options insuffisantes",
                "Vous devez fournir au moins 2 options séparées par des virgules."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if len(choices) > 20:
            embed = EmbedBuilder.error(
                "Trop d'options",
                "Vous ne pouvez pas avoir plus de 20 options."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Choix aléatoire
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Choix aléatoire",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📝 Options",
            value="\n".join([f"• {choice}" for choice in choices]),
            inline=False
        )
        
        embed.add_field(
            name="🎉 Choix",
            value=f"**{chosen}**",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rps", description="Joue à pierre-papier-ciseaux contre le bot")
    @app_commands.describe(choice="Votre choix")
    @app_commands.choices(choice=[
        app_commands.Choice(name="🗿 Pierre", value="pierre"),
        app_commands.Choice(name="📄 Papier", value="papier"),
        app_commands.Choice(name="✂️ Ciseaux", value="ciseaux")
    ])
    async def rps(self, interaction: discord.Interaction, choice: str):
        """Commande pierre-papier-ciseaux"""
        
        choices = ["pierre", "papier", "ciseaux"]
        bot_choice = random.choice(choices)
        
        # Emojis pour les choix
        emojis = {
            "pierre": "🗿",
            "papier": "📄",
            "ciseaux": "✂️"
        }
        
        # Détermination du gagnant
        if choice == bot_choice:
            result = "Égalité !"
            color = 0xffff00
        elif (choice == "pierre" and bot_choice == "ciseaux") or \
             (choice == "papier" and bot_choice == "pierre") or \
             (choice == "ciseaux" and bot_choice == "papier"):
            result = "Vous gagnez ! 🎉"
            color = 0x00ff00
        else:
            result = "Vous perdez ! 😢"
            color = 0xff0000
        
        embed = discord.Embed(
            title="🎮 Pierre-Papier-Ciseaux",
            description=result,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Votre choix",
            value=f"{emojis[choice]} {choice.title()}",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Choix du bot",
            value=f"{emojis[bot_choice]} {bot_choice.title()}",
            inline=True
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quote", description="Génère une citation inspirante aléatoire")
    async def quote(self, interaction: discord.Interaction):
        """Commande pour générer une citation inspirante"""
        
        quotes = [
            ("La vie, c'est comme une bicyclette, il faut avancer pour ne pas perdre l'équilibre.", "Albert Einstein"),
            ("Le succès, c'est d'aller d'échec en échec sans perdre son enthousiasme.", "Winston Churchill"),
            ("La seule façon de faire du bon travail, c'est d'aimer ce que vous faites.", "Steve Jobs"),
            ("L'imagination est plus importante que la connaissance.", "Albert Einstein"),
            ("Il n'y a qu'une façon d'échouer, c'est d'abandonner avant d'avoir réussi.", "Georges Clemenceau"),
            ("Le bonheur n'est pas quelque chose de tout fait. Il vient de vos propres actions.", "Dalaï Lama"),
            ("La différence entre l'ordinaire et l'extraordinaire, c'est ce petit 'extra'.", "Jimmy Johnson"),
            ("Ne remettez pas à demain ce que vous pouvez faire aujourd'hui.", "Benjamin Franklin"),
            ("La persévérance est la noblesse de l'obstination.", "Adrien Decourcelle"),
            ("Il vaut mieux viser la perfection et la manquer que viser l'imperfection et l'atteindre.", "Bertrand Russell")
        ]
        
        quote_text, author = random.choice(quotes)
        
        embed = discord.Embed(
            title="💭 Citation du jour",
            description=f"*\"{quote_text}\"*",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="✍️ Auteur",
            value=f"— {author}",
            inline=False
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="joke", description="Raconte une blague aléatoire")
    async def joke(self, interaction: discord.Interaction):
        """Commande pour raconter une blague"""
        
        jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon, ils tombent dans le bateau ! 😂",
            "Que dit un escargot quand il croise une limace ? 'Regarde, un nudiste !' 🐌",
            "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet ! 🐟",
            "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-mallow ! 🐱",
            "Que dit un informaticien quand il se noie ? F1 ! F1 ! ⌨️",
            "Pourquoi les développeurs préfèrent-ils le mode sombre ? Parce que la lumière attire les bugs ! 🐛",
            "Comment appelle-t-on un boomerang qui ne revient pas ? Un bâton ! 🪃",
            "Que dit un 0 à un 8 ? 'Joli ceinture !' 😄",
            "Pourquoi les mathématiciens confondent-ils Halloween et Noël ? Parce que 31 Oct = 25 Dec ! 🎃",
            "Comment appelle-t-on un chien qui n'a pas de pattes ? On ne l'appelle pas, on va le chercher ! 🐕"
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="😂 Blague du jour",
            description=joke,
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="compliment", description="Donne un compliment à quelqu'un")
    @app_commands.describe(member="La personne à complimenter")
    async def compliment(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Commande pour complimenter quelqu'un"""
        
        target = member or interaction.user
        
        compliments = [
            "est une personne formidable ! ✨",
            "a un sourire qui illumine la journée ! 😊",
            "est quelqu'un de très intelligent ! 🧠",
            "a un cœur en or ! 💛",
            "est une source d'inspiration ! 🌟",
            "a une personnalité magnifique ! 🌈",
            "est quelqu'un de très créatif ! 🎨",
            "a une énergie positive contagieuse ! ⚡",
            "est une personne très généreuse ! 🤗",
            "a un sens de l'humour fantastique ! 😄"
        ]
        
        compliment = random.choice(compliments)
        
        embed = discord.Embed(
            title="💝 Compliment",
            description=f"{target.mention} {compliment}",
            color=0xff69b4,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Compliment de {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="meme", description="Génère un mème textuel aléatoire")
    async def meme(self, interaction: discord.Interaction):
        """Commande pour générer un mème textuel"""
        
        memes = [
            {
                "title": "Drake qui pointe",
                "content": "❌ Faire ses devoirs\n✅ Regarder des mèmes sur Discord"
            },
            {
                "title": "Cerveau qui grandit",
                "content": "🧠 Utiliser un bot\n🧠🧠 Configurer un bot\n🧠🧠🧠 Créer un bot\n🧠🧠🧠🧠 Être le bot"
            },
            {
                "title": "Distracted Boyfriend",
                "content": "👫 Moi et mes responsabilités\n👀 Moi regardant Discord\n👩 Discord"
            },
            {
                "title": "This is Fine",
                "content": "🔥🐕🔥\n'Tout va bien'\n(Quand le serveur Discord est en panne)"
            },
            {
                "title": "Galaxy Brain",
                "content": "💭 Envoyer un message\n🧠 Envoyer un embed\n🌌 Envoyer un embed avec des réactions\n🌠 Créer un bot qui fait tout ça"
            }
        ]
        
        meme = random.choice(memes)
        
        embed = discord.Embed(
            title=f"😂 {meme['title']}",
            description=meme['content'],
            color=0xffd700,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(FunCog(bot))

