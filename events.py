import random
from colorama import Fore, Style
import time  # Add this import at the top

class EventResult:
    def __init__(self, end_simulation=False, points_override=None, message=None):
        self.end_simulation = end_simulation
        self.points_override = points_override
        self.message = message

class Event:
    def __init__(self, name, trigger_chance, condition_fn):
        self.name = name
        self.trigger_chance = trigger_chance  # Probability 0-1
        self.condition_fn = condition_fn      # Function that takes simulation state and returns bool
    
    def check_trigger(self, sim_state):
        if self.condition_fn(sim_state) and random.random() < self.trigger_chance:
            return self.execute(sim_state)
        return None
    
    def execute(self, sim_state):
        # Override in specific event classes
        pass

class DeathGameEvent(Event):
    def __init__(self):
        super().__init__(
            "Death Game",
            0.01,  # 1% chance
            lambda state: state['chosen_action']['name'].lower() == 'gamble'
        )
    
    def execute(self, sim_state):
        if not sim_state.get('quiet', True):  # Only show dramatic text if not in quiet mode
            print(f"{Fore.YELLOW}{Style.BRIGHT}A DEATH GAME IS COMMENCING!{Style.RESET_ALL}")
            time.sleep(5)
        
        if random.random() < 0.5:  # 50-50 chance
            return EventResult(
                end_simulation=True,
                points_override={'energy': 0, 'health': 0, 'happiness': 0},
                message=None if sim_state.get('quiet', True) else f"{Fore.RED}{Style.BRIGHT}THE DEATH GAME ENDED IN CATASTROPHIC LOSS!{Style.RESET_ALL}"
            )
        else:
            return EventResult(
                end_simulation=True,
                points_override={'energy': 50, 'health': 50, 'happiness': 50},
                message=None if sim_state.get('quiet', True) else f"{Fore.GREEN}{Style.BRIGHT}THE DEATH GAME RESULTED IN AN INCREDIBLE WIN!{Style.RESET_ALL}"
            )

# List of all available events
EVENTS = [
    DeathGameEvent(),
    # Add more events here
]