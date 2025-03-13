# config.py
from typing import Dict

GAME_CONFIG = {
    'BASE_ADDICTION': {
        "gambling": 0.425,
        "alcohol": 0,    
        "shopping": 0,
        "junk_food": 0
    },
    'BREAKDOWN': {
        'BASE_PENALTY': 5,
        'MULTIPLIER': 2.0
    },
    'STATS': {
        'MAX_VALUE': 50,
        'MIN_VALUE': 0
    },
    'SIMULATION': {
        'DEFAULT_STEPS': 10,
        'DEFAULT_RATIONALITY': 0.5,
        'DEFAULT_MONEY': 1000,
        'DEFAULT_ADDICTION_PRED': 1.0,
        'DEFAULT_RISK_TOLERANCE': 0.0
    }
}

DISPLAY_CONFIG = {
    'COLORS': {
        'low': 'RED',
        'medium': 'YELLOW',
        'high': 'GREEN'
    },
    'THRESHOLDS': {
        'low': 10,
        'medium': 35
    }
}