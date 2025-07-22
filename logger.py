"""
Module de logging pour Smiity Bot
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = 'smiity_bot', level: int = logging.INFO) -> logging.Logger:
    """Configure et retourne un logger pour Smiity Bot"""
    
    # Création du répertoire de logs
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier
    file_handler = logging.FileHandler(
        logs_dir / f'smiity_bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

