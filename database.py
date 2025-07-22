"""
Gestionnaire de base de données pour Smiity Bot
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, update, delete, and_

from .models import Base, Guild, User, Level, Economy, Moderation

logger = logging.getLogger(__name__)

class Database:
    """Gestionnaire de base de données pour Smiity Bot"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialise la connexion à la base de données"""
        try:
            # Conversion de l'URL pour asyncpg si nécessaire
            if self.database_url.startswith('postgresql://'):
                self.database_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
            elif self.database_url.startswith('sqlite:///'):
                self.database_url = self.database_url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)
            
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Création des tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Base de données initialisée avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    async def close(self):
        """Ferme la connexion à la base de données"""
        if self.engine:
            await self.engine.dispose()
            logger.info("🔒 Connexion à la base de données fermée")
    
    def get_session(self) -> AsyncSession:
        """Retourne une nouvelle session de base de données"""
        return self.session_factory()
    
    # Méthodes pour les guildes
    async def create_guild(self, guild_id: int, name: str) -> Guild:
        """Crée ou met à jour une guilde"""
        async with self.get_session() as session:
            # Vérifier si la guilde existe déjà
            result = await session.execute(
                select(Guild).where(Guild.id == guild_id)
            )
            guild = result.scalar_one_or_none()
            
            if guild:
                guild.name = name
            else:
                guild = Guild(id=guild_id, name=name)
                session.add(guild)
            
            await session.commit()
            return guild
    
    async def get_guild(self, guild_id: int) -> Optional[Guild]:
        """Récupère une guilde par son ID"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Guild).where(Guild.id == guild_id)
            )
            return result.scalar_one_or_none()
    
    # Méthodes pour les utilisateurs
    async def get_or_create_user(self, user_id: int, guild_id: int) -> User:
        """Récupère ou crée un utilisateur"""
        async with self.get_session() as session:
            result = await session.execute(
                select(User).where(
                    and_(User.id == user_id, User.guild_id == guild_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(id=user_id, guild_id=guild_id)
                session.add(user)
                await session.commit()
            
            return user
    
    # Méthodes pour les niveaux
    async def get_user_level(self, user_id: int, guild_id: int) -> Level:
        """Récupère le niveau d'un utilisateur"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Level).where(
                    and_(Level.user_id == user_id, Level.guild_id == guild_id)
                )
            )
            level = result.scalar_one_or_none()
            
            if not level:
                level = Level(user_id=user_id, guild_id=guild_id)
                session.add(level)
                await session.commit()
            
            return level
    
    async def add_xp(self, user_id: int, guild_id: int, xp_amount: int) -> Level:
        """Ajoute de l'XP à un utilisateur"""
        async with self.get_session() as session:
            level = await self.get_user_level(user_id, guild_id)
            level.xp += xp_amount
            level.messages_count += 1
            
            # Calcul du nouveau niveau
            new_level = self._calculate_level(level.xp)
            old_level = level.level
            level.level = new_level
            
            await session.commit()
            
            # Retourner si l'utilisateur a gagné un niveau
            level.level_up = new_level > old_level
            return level
    
    def _calculate_level(self, xp: int) -> int:
        """Calcule le niveau basé sur l'XP"""
        # Formule similaire à MEE6: niveau = racine(xp/100)
        import math
        return int(math.sqrt(xp / 100))
    
    # Méthodes pour l'économie
    async def get_user_economy(self, user_id: int, guild_id: int) -> Economy:
        """Récupère les données économiques d'un utilisateur"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Economy).where(
                    and_(Economy.user_id == user_id, Economy.guild_id == guild_id)
                )
            )
            economy = result.scalar_one_or_none()
            
            if not economy:
                economy = Economy(user_id=user_id, guild_id=guild_id)
                session.add(economy)
                await session.commit()
            
            return economy
    
    async def update_balance(self, user_id: int, guild_id: int, amount: int) -> Economy:
        """Met à jour le solde d'un utilisateur"""
        async with self.get_session() as session:
            economy = await self.get_user_economy(user_id, guild_id)
            economy.balance += amount
            await session.commit()
            return economy

