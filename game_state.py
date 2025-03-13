from dataclasses import dataclass
from typing import Dict, List

@dataclass
class GameState:
    current_points: Dict[str, float]
    current_addictions: Dict[str, float]
    zero_stat_turns: Dict[str, int]
    last_addiction_use: Dict[str, int]
    time_series: List[Dict[str, float]]
    addiction_levels: Dict[str, List[float]]
    addiction_overrides: Dict[str, int]
    was_death_game: bool = False
    
    @classmethod
    def create_initial(cls, initial_money: float, base_addictions: Dict[str, float], 
                      global_addiction_pred: float = 1.0):
        return cls(
            current_points={'energy': 10, 'health': 5, 'happiness': 5, 'money': initial_money},
            current_addictions={k: v * global_addiction_pred for k, v in base_addictions.items()},
            zero_stat_turns={'energy': 0, 'health': 0, 'happiness': 0},
            last_addiction_use={k: 0 for k in base_addictions},
            time_series=[],
            addiction_levels={k: [] for k in base_addictions},
            addiction_overrides={k: 0 for k in base_addictions}
        )