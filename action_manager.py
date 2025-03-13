import random
from typing import List, Dict, Tuple
from colorama import Fore, Style

def generate_action_pool(actions: List[Dict], size: int = 5) -> List[Dict]:
    return random.sample(actions, k=size)

def bias_pool_for_addictions(pool: List[Dict], current_addictions: Dict[str, float], 
                           all_actions: List[Dict]) -> List[Dict]:
    """Add addiction bias to action pool"""
    result = pool.copy()
    for addiction, level in current_addictions.items():
        if level > 0.3:
            bias_probability = min(1.0, (level - 0.3) / (0.7 - 0.3))
            if not any(act.get(f"{addiction}_addiction", 0) > 0 for act in result):
                if random.random() < bias_probability:
                    addictive_candidates = [act for act in all_actions 
                                         if act.get(f"{addiction}_addiction", 0) > 0]
                    if addictive_candidates:
                        forced_action = random.choice(addictive_candidates)
                        replace_idx = random.randint(0, len(result) - 1)
                        result[replace_idx] = forced_action
    return result