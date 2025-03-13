from typing import Dict, Tuple
from colorama import Fore, Style
import random

def check_addiction_triggers(current_addictions: Dict[str, float], 
                           pool: List[Dict]) -> List[Tuple[str, Dict]]:
    """Check for addiction overrides"""
    triggered_overrides = []
    for addiction, level in current_addictions.items():
        if level >= 0.95:
            addictive_actions = [act for act in pool 
                               if act.get(f"{addiction}_addiction", 0) > 0]
            if addictive_actions:
                triggered_overrides.append((addiction, random.choice(addictive_actions)))
        elif random.random() < level:
            addictive_actions = [act for act in pool 
                               if act.get(f"{addiction}_addiction", 0) > 0]
            if addictive_actions:
                triggered_overrides.append((addiction, random.choice(addictive_actions)))
    return triggered_overrides