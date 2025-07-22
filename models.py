"""
Modèles de base de données pour Smiity Bot
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Guild(Base):
    """Modèle pour les serveurs Discord"""
    __tablename__ = 'guilds'
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    
    # Configuration des modules
    moderation_enabled = Column(Boolean, default=True)
    levels_enabled = Column(Boolean, default=True)
    economy_enabled = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=False)
    logs_enabled = Column(Boolean, default=False)
    
    # Configuration des canaux
    welcome_channel_id = Column(BigInteger, nullable=True)
    logs_channel_id = Column(BigInteger, nullable=True)
    
    # Configuration des rôles
    moderator_role_id = Column(BigInteger, nullable=True)
    muted_role_id = Column(BigInteger, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """Modèle pour les utilisateurs Discord"""
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Level(Base):
    """Modèle pour le système de niveaux"""
    __tablename__ = 'levels'
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    
    level = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Economy(Base):
    """Modèle pour le système d'économie"""
    __tablename__ = 'economy'
    
    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    
    balance = Column(Integer, default=0)
    bank = Column(Integer, default=0)
    
    # Système de daily
    daily_streak = Column(Integer, default=0)
    last_daily = Column(DateTime, nullable=True)
    
    # Statistiques
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Moderation(Base):
    """Modèle pour les actions de modération"""
    __tablename__ = 'moderation'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    
    action_type = Column(String(20), nullable=False)  # kick, ban, mute, warn, etc.
    reason = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # en secondes pour les mutes temporaires
    expires_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomCommand(Base):
    """Modèle pour les commandes personnalisées"""
    __tablename__ = 'custom_commands'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), nullable=False)
    
    name = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    creator_id = Column(BigInteger, nullable=False)
    uses = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

