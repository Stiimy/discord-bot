"""
Module d'économie pour Smiity Bot
Système d'économie avec coins, daily, boutique comme DraftBot
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import random

from embeds import EmbedBuilder

class EconomyCog(commands.Cog):
    """Cog pour le système d'économie"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="balance", description="Affiche votre solde ou celui d'un autre membre")
    @app_commands.describe(member="Le membre dont vous voulez voir le solde")
    async def balance(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Commande pour afficher le solde d'un utilisateur"""
        
        target = member or interaction.user
        
        try:
            # Récupération des données économiques
            economy_data = await self.bot.db.get_user_economy(target.id, interaction.guild.id)
            
            # Création de l'embed de profil économique
            embed = EmbedBuilder.economy_profile(
                target,
                economy_data.balance,
                economy_data.bank,
                economy_data.daily_streak
            )
            
            # Ajout d'informations supplémentaires
            embed.add_field(
                name="📊 Statistiques",
                value=(
                    f"**Total gagné:** {economy_data.total_earned:,} coins\n"
                    f"**Total dépensé:** {economy_data.total_spent:,} coins"
                ),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de récupérer les données économiques: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="daily", description="Récupère votre récompense quotidienne")
    async def daily(self, interaction: discord.Interaction):
        """Commande pour récupérer la récompense quotidienne"""
        
        try:
            # Récupération des données économiques
            economy_data = await self.bot.db.get_user_economy(interaction.user.id, interaction.guild.id)
            
            # Vérification si l'utilisateur peut récupérer sa récompense
            now = datetime.utcnow()
            if economy_data.last_daily:
                time_since_last = now - economy_data.last_daily
                if time_since_last < timedelta(hours=20):  # 20h au lieu de 24h pour être généreux
                    next_daily = economy_data.last_daily + timedelta(hours=20)
                    remaining = next_daily - now
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    
                    embed = EmbedBuilder.warning(
                        "Récompense déjà récupérée",
                        f"Vous avez déjà récupéré votre récompense quotidienne !\n"
                        f"⏰ Prochaine récompense dans: **{hours}h {minutes}m**"
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            # Calcul de la récompense
            base_reward = 100
            streak_bonus = min(economy_data.daily_streak * 10, 100)  # Max 100 coins de bonus
            total_reward = base_reward + streak_bonus
            
            # Vérification de la série (si moins de 48h depuis le dernier daily)
            if economy_data.last_daily and (now - economy_data.last_daily) < timedelta(hours=48):
                economy_data.daily_streak += 1
            else:
                economy_data.daily_streak = 1
            
            # Mise à jour des données
            economy_data.balance += total_reward
            economy_data.total_earned += total_reward
            economy_data.last_daily = now
            
            # Sauvegarde en base de données
            async with self.bot.db.get_session() as session:
                session.add(economy_data)
                await session.commit()
            
            # Réponse de confirmation
            embed = discord.Embed(
                title="💰 Récompense quotidienne récupérée !",
                description=f"Vous avez reçu **{total_reward:,} coins** !",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="💵 Récompense de base",
                value=f"{base_reward:,} coins",
                inline=True
            )
            
            if streak_bonus > 0:
                embed.add_field(
                    name="🔥 Bonus de série",
                    value=f"{streak_bonus:,} coins",
                    inline=True
                )
            
            embed.add_field(
                name="🔥 Série actuelle",
                value=f"{economy_data.daily_streak} jours",
                inline=True
            )
            
            embed.add_field(
                name="💎 Nouveau solde",
                value=f"{economy_data.balance:,} coins",
                inline=False
            )
            
            embed.set_footer(text="Revenez demain pour continuer votre série !")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de récupérer la récompense quotidienne: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="pay", description="Donne des coins à un autre membre")
    @app_commands.describe(
        member="Le membre à qui donner des coins",
        amount="Quantité de coins à donner"
    )
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Commande pour donner des coins à un autre membre"""
        
        if member.bot:
            embed = EmbedBuilder.error(
                "Membre invalide",
                "Vous ne pouvez pas donner des coins à un bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = EmbedBuilder.error(
                "Action invalide",
                "Vous ne pouvez pas vous donner des coins à vous-même."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount <= 0:
            embed = EmbedBuilder.error(
                "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Récupération des données économiques
            sender_data = await self.bot.db.get_user_economy(interaction.user.id, interaction.guild.id)
            receiver_data = await self.bot.db.get_user_economy(member.id, interaction.guild.id)
            
            # Vérification du solde
            if sender_data.balance < amount:
                embed = EmbedBuilder.error(
                    "Solde insuffisant",
                    f"Vous n'avez que **{sender_data.balance:,} coins**. Vous ne pouvez pas donner **{amount:,} coins**."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Transaction
            sender_data.balance -= amount
            sender_data.total_spent += amount
            receiver_data.balance += amount
            receiver_data.total_earned += amount
            
            # Sauvegarde en base de données
            async with self.bot.db.get_session() as session:
                session.add(sender_data)
                session.add(receiver_data)
                await session.commit()
            
            # Réponse de confirmation
            embed = EmbedBuilder.success(
                "Transaction réussie",
                f"✅ Vous avez donné **{amount:,} coins** à {member.mention} !\n\n"
                f"**Votre nouveau solde:** {sender_data.balance:,} coins\n"
                f"**Solde de {member.display_name}:** {receiver_data.balance:,} coins"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible d'effectuer la transaction: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="rob", description="Tentez de voler des coins à un autre membre")
    @app_commands.describe(member="Le membre à voler")
    async def rob(self, interaction: discord.Interaction, member: discord.Member):
        """Commande pour voler des coins à un autre membre"""
        
        if member.bot:
            embed = EmbedBuilder.error(
                "Membre invalide",
                "Vous ne pouvez pas voler un bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = EmbedBuilder.error(
                "Action invalide",
                "Vous ne pouvez pas vous voler vous-même."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Récupération des données économiques
            robber_data = await self.bot.db.get_user_economy(interaction.user.id, interaction.guild.id)
            victim_data = await self.bot.db.get_user_economy(member.id, interaction.guild.id)
            
            # Vérifications
            if robber_data.balance < 100:
                embed = EmbedBuilder.error(
                    "Solde insuffisant",
                    "Vous devez avoir au moins **100 coins** pour tenter un vol."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if victim_data.balance < 50:
                embed = EmbedBuilder.warning(
                    "Cible trop pauvre",
                    f"{member.display_name} n'a pas assez de coins pour être volé (minimum 50 coins)."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Calcul des chances de succès (50% de base)
            success_chance = 0.5
            success = random.random() < success_chance
            
            if success:
                # Vol réussi
                stolen_amount = random.randint(10, min(victim_data.balance // 4, 500))
                
                robber_data.balance += stolen_amount
                robber_data.total_earned += stolen_amount
                victim_data.balance -= stolen_amount
                victim_data.total_spent += stolen_amount
                
                embed = EmbedBuilder.success(
                    "Vol réussi !",
                    f"🎉 Vous avez volé **{stolen_amount:,} coins** à {member.mention} !\n\n"
                    f"**Votre nouveau solde:** {robber_data.balance:,} coins"
                )
                
            else:
                # Vol échoué
                fine_amount = random.randint(50, min(robber_data.balance // 4, 200))
                
                robber_data.balance -= fine_amount
                robber_data.total_spent += fine_amount
                
                embed = EmbedBuilder.error(
                    "Vol échoué !",
                    f"💸 Vous avez été attrapé ! Vous payez une amende de **{fine_amount:,} coins**.\n\n"
                    f"**Votre nouveau solde:** {robber_data.balance:,} coins"
                )
            
            # Sauvegarde en base de données
            async with self.bot.db.get_session() as session:
                session.add(robber_data)
                session.add(victim_data)
                await session.commit()
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible d'effectuer le vol: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="work", description="Travaillez pour gagner des coins")
    async def work(self, interaction: discord.Interaction):
        """Commande pour travailler et gagner des coins"""
        
        try:
            # Récupération des données économiques
            economy_data = await self.bot.db.get_user_economy(interaction.user.id, interaction.guild.id)
            
            # Vérification du cooldown (1 heure)
            now = datetime.utcnow()
            if hasattr(economy_data, 'last_work') and economy_data.last_work:
                time_since_last = now - economy_data.last_work
                if time_since_last < timedelta(hours=1):
                    remaining = timedelta(hours=1) - time_since_last
                    minutes = int(remaining.total_seconds() // 60)
                    
                    embed = EmbedBuilder.warning(
                        "Vous êtes fatigué",
                        f"Vous devez attendre encore **{minutes} minutes** avant de pouvoir retravailler."
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            # Génération d'un travail aléatoire
            jobs = [
                ("développeur", "Vous avez codé une application", (80, 150)),
                ("livreur", "Vous avez livré des pizzas", (40, 80)),
                ("streamer", "Vous avez fait un live", (60, 120)),
                ("professeur", "Vous avez donné des cours", (70, 130)),
                ("artiste", "Vous avez vendu une œuvre", (50, 200)),
                ("mécanicien", "Vous avez réparé une voiture", (90, 140)),
                ("cuisinier", "Vous avez préparé des plats", (60, 110)),
                ("jardinier", "Vous avez entretenu un jardin", (45, 85))
            ]
            
            job_name, job_description, (min_pay, max_pay) = random.choice(jobs)
            earned = random.randint(min_pay, max_pay)
            
            # Mise à jour des données
            economy_data.balance += earned
            economy_data.total_earned += earned
            # Note: last_work devrait être ajouté au modèle Economy
            
            # Sauvegarde en base de données
            async with self.bot.db.get_session() as session:
                session.add(economy_data)
                await session.commit()
            
            # Réponse de confirmation
            embed = discord.Embed(
                title="💼 Travail terminé !",
                description=f"{job_description} et avez gagné **{earned:,} coins** !",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="👔 Métier",
                value=job_name.title(),
                inline=True
            )
            
            embed.add_field(
                name="💰 Gains",
                value=f"{earned:,} coins",
                inline=True
            )
            
            embed.add_field(
                name="💎 Nouveau solde",
                value=f"{economy_data.balance:,} coins",
                inline=True
            )
            
            embed.set_footer(text="Vous pourrez retravailler dans 1 heure !")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de travailler: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="coinflip", description="Pariez sur pile ou face")
    @app_commands.describe(
        choice="Votre choix (pile ou face)",
        amount="Montant à parier"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Pile", value="pile"),
        app_commands.Choice(name="Face", value="face")
    ])
    async def coinflip(self, interaction: discord.Interaction, choice: str, amount: int):
        """Commande pour jouer à pile ou face"""
        
        if amount <= 0:
            embed = EmbedBuilder.error(
                "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount > 10000:
            embed = EmbedBuilder.error(
                "Montant trop élevé",
                "Vous ne pouvez pas parier plus de 10,000 coins."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Récupération des données économiques
            economy_data = await self.bot.db.get_user_economy(interaction.user.id, interaction.guild.id)
            
            # Vérification du solde
            if economy_data.balance < amount:
                embed = EmbedBuilder.error(
                    "Solde insuffisant",
                    f"Vous n'avez que **{economy_data.balance:,} coins**. Vous ne pouvez pas parier **{amount:,} coins**."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Lancement de la pièce
            result = random.choice(["pile", "face"])
            won = choice == result
            
            # Mise à jour du solde
            if won:
                economy_data.balance += amount
                economy_data.total_earned += amount
                color = 0x00ff00
                title = "🎉 Vous avez gagné !"
                description = f"La pièce est tombée sur **{result}** !\nVous gagnez **{amount:,} coins** !"
            else:
                economy_data.balance -= amount
                economy_data.total_spent += amount
                color = 0xff0000
                title = "😢 Vous avez perdu !"
                description = f"La pièce est tombée sur **{result}** !\nVous perdez **{amount:,} coins** !"
            
            # Sauvegarde en base de données
            async with self.bot.db.get_session() as session:
                session.add(economy_data)
                await session.commit()
            
            # Réponse
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🪙 Résultat",
                value=result.title(),
                inline=True
            )
            
            embed.add_field(
                name="💎 Nouveau solde",
                value=f"{economy_data.balance:,} coins",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de jouer: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="richest", description="Affiche les membres les plus riches du serveur")
    @app_commands.describe(page="Page du classement à afficher")
    async def richest(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """Commande pour afficher le classement des plus riches"""
        
        if page < 1:
            page = 1
        
        try:
            # Récupération du top des utilisateurs les plus riches
            top_users = await self._get_richest_users(interaction.guild.id, page)
            
            if not top_users:
                embed = EmbedBuilder.info(
                    "Classement vide",
                    "Aucun utilisateur n'a encore de coins sur ce serveur."
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Création de l'embed de classement
            embed = discord.Embed(
                title="💰 Classement des plus riches",
                description=f"Top des membres les plus riches de **{interaction.guild.name}**",
                color=0xffd700,
                timestamp=datetime.utcnow()
            )
            
            leaderboard_text = []
            start_rank = (page - 1) * 10 + 1
            
            for i, user_data in enumerate(top_users, start=start_rank):
                # Récupération du membre Discord
                try:
                    member = interaction.guild.get_member(user_data['user_id'])
                    if member:
                        username = member.display_name
                    else:
                        username = f"Utilisateur {user_data['user_id']}"
                except:
                    username = f"Utilisateur {user_data['user_id']}"
                
                # Emoji de médaille
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                total_wealth = user_data['balance'] + user_data['bank']
                leaderboard_text.append(
                    f"{medal} **{username}** - {total_wealth:,} coins"
                )
            
            embed.description += f"\n\n" + "\n".join(leaderboard_text)
            embed.set_footer(text=f"Page {page} • Utilisez /richest <page> pour naviguer")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                "Erreur",
                f"Impossible de récupérer le classement: {str(e)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _get_richest_users(self, guild_id: int, page: int = 1, limit: int = 10) -> List[Dict]:
        """Récupère le top des utilisateurs les plus riches"""
        try:
            offset = (page - 1) * limit
            
            async with self.bot.db.get_session() as session:
                from database.models import Economy
                from sqlalchemy import select
                
                result = await session.execute(
                    select(Economy).where(
                        Economy.guild_id == guild_id
                    ).order_by((Economy.balance + Economy.bank).desc()).offset(offset).limit(limit)
                )
                
                economies = result.scalars().all()
                
                return [
                    {
                        'user_id': economy.user_id,
                        'balance': economy.balance,
                        'bank': economy.bank,
                        'daily_streak': economy.daily_streak
                    }
                    for economy in economies
                ]
                
        except Exception as e:
            self.bot.logger.error(f"Erreur lors de la récupération du top richest: {e}")
            return []

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(EconomyCog(bot))

