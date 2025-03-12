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
            None,  # We'll calculate trigger chance dynamically
            lambda state: state['chosen_action']['name'].lower() == 'gamble'
        )
    
    def check_trigger(self, sim_state):
        # Calculate trigger chance based on risk tolerance
        risk_tolerance = sim_state.get('risk_tolerance', 0.0)  # Default to neutral if not provided
        # Convert risk_tolerance from [-1,1] to [0,1] then scale between 0.001 (0.1%) and 0.05 (5%)
        base_chance = 0.001 + ((risk_tolerance + 1) / 2) * (0.05 - 0.001)
        
        if self.condition_fn(sim_state) and random.random() < base_chance:
            return self.execute(sim_state)
        return None
    
    def execute(self, sim_state):
        if not sim_state.get('quiet', True):
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