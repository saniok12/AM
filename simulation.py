import random
from actions import actions
from colorama import init, Fore, Style
from events import EVENTS, DeathGameEvent
from economy import compute_money_weight, color_money
from risk import calculate_risk_adjusted_values
from gambling import execute_gambling
from utils import clamp
from game_state import GameState
from action_manager import generate_action_pool, bias_pool_for_addictions
from addiction_system import check_addiction_triggers
from display import format_action_display, show_stats, color_points, color_cost
from config import GAME_CONFIG

init()  # Initialize colorama for colored terminal output

def clamp(value, min_value=0, max_value=50):
    return max(min_value, min(max_value, value))

def compute_weighted_sum(action, current_points):
    total = 0
    # Calculate base weights from energy/health/happiness
    for key in ['energy', 'health', 'happiness']:
        factor = 1 - (current_points[key] / 50)
        total += factor * action[key]
    
    # Add money weight if present
    if 'money' in current_points:
        # Remove the gambling penalization since addiction override should work regardless of money
        total += compute_money_weight(action, current_points['money'])
    
    return total

def calculate_breakdown_penalty(turns_at_zero):
    """Calculate exponentially increasing happiness penalty."""
    return min(GAME_CONFIG['STATS']['MAX_VALUE'], 
              GAME_CONFIG['BREAKDOWN']['BASE_PENALTY'] * 
              (GAME_CONFIG['BREAKDOWN']['MULTIPLIER'] ** (turns_at_zero - 1)))

def check_and_apply_penalties(current_points: dict, zero_stat_turns: dict, quiet: bool = False) -> dict:
    """Check each stat and apply penalties if at zero"""
    result = current_points.copy()
    
    for stat in ['energy', 'health', 'happiness']:
        if result[stat] == 0:
            zero_stat_turns[stat] += 1
            penalty = calculate_breakdown_penalty(zero_stat_turns[stat])
            
            if stat == 'energy':
                if not quiet:
                    print(f"{Fore.RED}Warning: Zero energy for {zero_stat_turns[stat]} turns! -{penalty} health and happiness{Style.RESET_ALL}")
                result['health'] = max(0, result['health'] - penalty)
                result['happiness'] = max(0, result['happiness'] - penalty)
            elif stat == 'happiness':
                if not quiet:
                    print(f"{Fore.RED}Warning: Zero happiness for {zero_stat_turns[stat]} turns! -{penalty} health{Style.RESET_ALL}")
                result['health'] = max(0, result['health'] - penalty)
            elif stat == 'health':
                if not quiet:
                    print(f"{Fore.RED}Warning: Zero health for {zero_stat_turns[stat]} turns! -{penalty} energy and happiness{Style.RESET_ALL}")
                result['energy'] = max(0, result['energy'] - penalty)
                result['happiness'] = max(0, result['happiness'] - penalty)
        else:
            zero_stat_turns[stat] = 0
            
    return result

def simulate_run(rationality, initial_money, risk_tolerance=GAME_CONFIG['SIMULATION']['DEFAULT_RISK_TOLERANCE'], 
                steps=GAME_CONFIG['SIMULATION']['DEFAULT_STEPS'], 
                manual_mode=False, quiet=False, record_actions=False, 
                global_addiction_pred=GAME_CONFIG['SIMULATION']['DEFAULT_ADDICTION_PRED']):
    """Run a single simulation with given parameters."""
    state = GameState.create_initial(initial_money, GAME_CONFIG['BASE_ADDICTION'], global_addiction_pred)
    
    for move in range(1, steps + 1):
        show_stats(state.current_points, quiet)
        pool = generate_action_pool(actions)
        pool = bias_pool_for_addictions(pool, state.current_addictions, actions)
        # ... rest of simulation logic

def interactive_mode():
    while True:  # Main interaction loop
        try:
            rationality = float(input("Enter rationality (0 to 1): "))
            if not 0 <= rationality <= 1:
                raise ValueError
        except ValueError:
            print(f"Invalid input. Using default rationality of {GAME_CONFIG['SIMULATION']['DEFAULT_RATIONALITY']}")
            rationality = GAME_CONFIG['SIMULATION']['DEFAULT_RATIONALITY']

        try:
            steps = int(input("Enter number of moves (steps): "))
        except ValueError:
            print(f"Invalid input. Using default of {GAME_CONFIG['SIMULATION']['DEFAULT_STEPS']} moves.")
            steps = GAME_CONFIG['SIMULATION']['DEFAULT_STEPS']

        try:
            initial_money = float(input("Enter initial money amount: "))
        except ValueError:
            print(f"Invalid input. Using default of {GAME_CONFIG['SIMULATION']['DEFAULT_INITIAL_MONEY']} money")
            initial_money = GAME_CONFIG['SIMULATION']['DEFAULT_INITIAL_MONEY']

        try:
            global_addiction_pred = float(input("Enter global addiction predisposition multiplier: "))
        except ValueError:
            print(f"Invalid input. Using default predisposition of {GAME_CONFIG['SIMULATION']['DEFAULT_ADDICTION_PRED']}")
            global_addiction_pred = GAME_CONFIG['SIMULATION']['DEFAULT_ADDICTION_PRED']

        last_parameters = (rationality, steps, global_addiction_pred, initial_money)

        try:
            risk_tolerance = float(input("Enter risk tolerance (-1 to 1): "))
            if not -1 <= risk_tolerance <= 1:
                raise ValueError
        except ValueError:
            print(f"Invalid input. Using neutral risk tolerance ({GAME_CONFIG['SIMULATION']['DEFAULT_RISK_TOLERANCE']})")
            risk_tolerance = GAME_CONFIG['SIMULATION']['DEFAULT_RISK_TOLERANCE']

        while True:
            manual_input = input("Do you want manual mode? (1 for yes, 0 for no): ")
            manual_mode = True if manual_input == "1" else False

            # Save the current parameters to allow repeats with the same values
            last_parameters = (rationality, steps, manual_mode, global_addiction_pred, initial_money)

            # Display initial effective addiction levels
            print("Initial effective addiction levels:")
            for addiction in GAME_CONFIG['BASE_ADDICTION']:
                base_val = GAME_CONFIG['BASE_ADDICTION'][addiction]
                if base_val > 0:
                    effective_val = base_val * global_addiction_pred
                    print(f"  {addiction}: {Fore.GREEN}{effective_val*100:.1f}%{Style.RESET_ALL}")

            # Run the simulation
            simulate_run(rationality, initial_money, risk_tolerance=risk_tolerance, 
                         steps=steps, manual_mode=manual_mode, quiet=False, 
                         record_actions=True, global_addiction_pred=global_addiction_pred)

            # Only ask about repeating after the simulation is completely finished
            if not manual_mode:  # Only offer repeats in auto mode
                repeat = input("\nHow many times to repeat the simulation? (0 for none): ")
                try:
                    repeat = int(repeat)
                except ValueError:
                    print("Invalid input. Not repeating the simulation.")
                    repeat = 0

                if repeat > 1:
                    for _ in range(repeat - 1):
                        simulate_run(rationality, initial_money, risk_tolerance=risk_tolerance, 
                                   steps=steps, manual_mode=False, quiet=False, 
                                   record_actions=True, global_addiction_pred=global_addiction_pred)

            # Ask if user wants to start a new simulation with new parameters
            new_sim = input("\nStart new simulation with different parameters? (1 for yes, 0 for no): ")
            if new_sim != "1":
                break

if __name__ == "__main__":
    interactive_mode()
