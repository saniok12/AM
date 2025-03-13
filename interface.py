from colorama import Fore, Style
from config import GAME_CONFIG
from simulation import simulate_run

def interactive_mode():
    """Handle user interaction and simulation parameter input."""
    while True:  # Main interaction loop
        params = get_simulation_parameters()
        while True:
            run_simulation_with_parameters(params)
            if not handle_simulation_repeat(params):
                break
            
def get_simulation_parameters():
    """Get all simulation parameters from user input."""
    # Move parameter collection logic here
    
def run_simulation_with_parameters(params):
    """Run simulation with given parameters."""
    # Move simulation running logic here
    
def handle_simulation_repeat(params):
    """Handle simulation repeat logic."""
    # Move repeat handling logic here