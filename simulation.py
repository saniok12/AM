import random
from actions import actions
from colorama import init, Fore, Style
from events import EVENTS, DeathGameEvent  # Add this import at the top
from economy import compute_money_weight  # Add at top with other imports
from economy import color_money
from risk import calculate_risk_adjusted_values  # Add to imports
from gambling import execute_gambling  # Add to imports

init()  # Initialize colorama for colored terminal output

# Base addiction chances for each type.
BASE_ADDICTION = {
    "gambling": 0.1,
    "alcohol": 0.2,    
    "shopping": 0.1,
    "junk_food": 0.05
}

# Add these constants at the top of the file after BASE_ADDICTION
BREAKDOWN_BASE_PENALTY = 5
BREAKDOWN_MULTIPLIER = 2.0  # Each turn at zero doubles the penalty

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
        total += compute_money_weight(action, current_points['money'])
    
    return total

def color_points(value):
    """Color the numeric points based on thresholds."""
    if value < 10:
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    elif value < 35:
        return f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
    else:
        return f"{Fore.GREEN}{value}{Style.RESET_ALL}"

def color_cost(amount):
    """Color the cost in brackets: positive in green, negative in red, zero in default."""
    if amount > 0:
        return f"{Fore.GREEN}+{amount}{Style.RESET_ALL}"
    elif amount < 0:
        return f"{Fore.RED}{amount}{Style.RESET_ALL}"
    else:
        return f"{amount}"

# Add this function after the existing helper functions
def calculate_breakdown_penalty(turns_at_zero):
    """Calculate exponentially increasing happiness penalty."""
    return min(50, BREAKDOWN_BASE_PENALTY * (BREAKDOWN_MULTIPLIER ** (turns_at_zero - 1)))

def simulate_run(rationality, initial_money, risk_tolerance=0.0, steps=10, manual_mode=False, quiet=False, record_actions=False, global_addiction_pred=1.0):
    """Add risk_tolerance parameter with default neutral value"""
    # Initialize current addiction levels multiplicatively.
    current_addictions = {}
    for addiction in BASE_ADDICTION:
        base_value = BASE_ADDICTION[addiction]
        current_addictions[addiction] = base_value * global_addiction_pred

    last_addiction_use = {k: 0 for k in BASE_ADDICTION}  # Track moves since last use

    current_points = {'energy': 10, 'health': 5, 'happiness': 5, 'money': initial_money}
    time_series = []
    rational_count = 0
    random_count = 0
    chosen_actions_list = [] if record_actions else None

    addiction_overrides = {k: 0 for k in BASE_ADDICTION}  # Track override counts
    addiction_levels = {k: [] for k in BASE_ADDICTION}    # Track addiction progression

    # In simulate_run, add after initialization:
    # Track how many turns stats have been at zero
    zero_stat_turns = {'energy': 0, 'health': 0}

    # Add was_death_game flag
    was_death_game = False

    for move in range(1, steps + 1):
        if not quiet:
            # Color-coded display of current points
            c_energy = color_points(current_points['energy'])
            c_health = color_points(current_points['health'])
            c_happiness = color_points(current_points['happiness'])
            print(f"\nMove {move}: Current points: {{'energy': {c_energy}, 'health': {c_health}, 'happiness': {c_happiness}}}")

        # Generate a pool of 5 unique actions.
        pool = random.sample(actions, k=5)
        
        # --- Bias the pool for addictive actions based on addiction levels ---
        for addiction in current_addictions:
            level = current_addictions[addiction]
            if level > 0.3:
                bias_probability = min(1.0, (level - 0.3) / (0.7 - 0.3))
                if not any(act.get(f"{addiction}_addiction", 0) > 0 for act in pool):
                    if random.random() < bias_probability:
                        addictive_candidates = [act for act in actions if act.get(f"{addiction}_addiction", 0) > 0]
                        if addictive_candidates:
                            forced_action = random.choice(addictive_candidates)
                            replace_idx = random.randint(0, len(pool) - 1)
                            pool[replace_idx] = forced_action
        
        weighted_scores = [compute_weighted_sum(action, current_points) for action in pool]

        # --- Addiction Override Check ---
        triggered_overrides = []
        for addiction in current_addictions:
            effective_chance = current_addictions[addiction]
            
            # If addiction level is very high (threshold can be tweaked), force override if possible.
            if effective_chance >= 0.95:
                addictive_actions = [act for act in pool if act.get(f"{addiction}_addiction", 0) > 0]
                if addictive_actions:
                    triggered_overrides.append((addiction, random.choice(addictive_actions)))
            else:
                roll = random.random()
                if roll < effective_chance:
                    addictive_actions = [act for act in pool if act.get(f"{addiction}_addiction", 0) > 0]
                    if addictive_actions:
                        triggered_overrides.append((addiction, random.choice(addictive_actions)))

        if triggered_overrides:
            override_type, addiction_override = random.choice(triggered_overrides)
            addiction_overrides[override_type] += 1  # Count override
            
            # Tolerance-based growth: slower increase at higher levels
            base_increase = addiction_override.get(f"{override_type}_addiction", 0)
            current_level = current_addictions[override_type]
            
            if current_level > 0.7:  # High tolerance zone
                # Diminishing returns: much smaller increases at high levels
                tolerance_factor = 1 - (current_level - 0.7) / 0.3  # Scales from 1 to 0 as level goes from 0.7 to 1.0
                effective_increase = base_increase * tolerance_factor * 0.2  # Significantly reduced growth
            elif current_level > 0.4:  # Medium tolerance zone
                # Moderate slowdown in growth
                tolerance_factor = 1 - (current_level - 0.4) / 0.6  # Scales from 1 to 0 as level goes from 0.4 to 1.0
                effective_increase = base_increase * tolerance_factor * 0.5
            else:  # Low tolerance zone
                # Initial addiction builds relatively quickly
                effective_increase = base_increase
            
            current_addictions[override_type] = min(
                1.0,
                current_level + effective_increase
            )
            
            if not quiet:
                print(f"{Fore.MAGENTA}Addiction override triggered for {override_type}! (roll below {current_addictions[override_type]:.2f}){Style.RESET_ALL}")
            chosen_action = addiction_override
            decision_type = f"{Fore.MAGENTA}Addiction Override ({override_type}){Style.RESET_ALL}"
            if not quiet:
                print(f"{Fore.MAGENTA}The AI has become more addicted to {override_type}; its addiction level is now {current_addictions[override_type]*100:.1f}%{Style.RESET_ALL}")
        else:
            # Normal decision-making
            if random.random() < rationality:
                max_score = max(weighted_scores)
                best_indices = [i for i, score in enumerate(weighted_scores) if score == max_score]
                chosen_index = random.choice(best_indices)
                chosen_action = pool[chosen_index]
                decision_type = f"{Fore.CYAN}Rational (Best Choice){Style.RESET_ALL}"
                rational_count += 1
            else:
                chosen_action = random.choice(pool)
                decision_type = f"{Fore.YELLOW}Random Choice{Style.RESET_ALL}"
                random_count += 1

            # Check if chosen action is addictive for any type
            for addiction in current_addictions:
                incr = chosen_action.get(f"{addiction}_addiction", 0)
                if incr > 0:
                    current_addictions[addiction] = min(current_addictions[addiction] + incr, 1.0)
                    if not quiet:
                        print(f"{Fore.MAGENTA}The AI has become more addicted to {addiction}; its addiction level is now {current_addictions[addiction]*100:.1f}%{Style.RESET_ALL}")

        # In the simulate_run function, modify the action display section:
        if not quiet:
            print("Available actions:")
            for idx, action in enumerate(pool):
                # Color the cost in brackets
                e_str = color_cost(action['energy'])
                h_str = color_cost(action['health'])
                happ_str = color_cost(action['happiness'])
                money_str = color_cost(action.get('money', 0)) if 'money' in action else ""

                # Build a string for addiction info if present
                addiction_info = ""
                for addiction in ["alcohol", "gambling", "shopping", "junk_food"]:
                    incr = action.get(f"{addiction}_addiction", 0)
                    if incr:
                        addiction_info += f" Addiction: {addiction} (+{incr})"

                # Add money to display if present
                money_display = f", money: {money_str}" if 'money' in action else ""
                
                print(f"  {idx+1}. {action['name']} (Weighted Sum: {weighted_scores[idx]:.2f}) "
                      f"[energy: {e_str}, health: {h_str}, happiness: {happ_str}{money_display}]{addiction_info}")

            print(f"Chosen action: {chosen_action['name']} - {decision_type}")

        # Modify the points update section in the main simulation loop:
        # Update points and check for breakdown conditions
        if chosen_action['name'] == "gamble":
            # Execute gambling system - force quiet=False in interactive mode
            current_points = execute_gambling(
                current_points,
                risk_tolerance,
                current_addictions['gambling'],
                quiet=False if not manual_mode else quiet  # Always show gambling results in manual mode
            )
        else:
            # Normal action processing
            adjusted_values = calculate_risk_adjusted_values(chosen_action, risk_tolerance)
            for key in ['energy', 'health', 'happiness']:
                current_points[key] = clamp(current_points[key] + adjusted_values[key])
            if 'money' in adjusted_values:
                current_points['money'] += adjusted_values['money']
        
        # Apply breakdown penalties
        for stat in ['energy', 'health']:
            if current_points[stat] == 0:
                zero_stat_turns[stat] += 1
                penalty = calculate_breakdown_penalty(zero_stat_turns[stat])
                if not quiet:
                    print(f"{Fore.RED}Warning: Zero {stat} for {zero_stat_turns[stat]} turns! -{penalty} happiness{Style.RESET_ALL}")
                current_points['happiness'] = max(0, current_points['happiness'] - penalty)
            else:
                zero_stat_turns[stat] = 0
        
        # Check for events after action is chosen
        sim_state = {
            'current_points': current_points,
            'chosen_action': chosen_action,
            'current_addictions': current_addictions,
            'move': move
        }

        for event in EVENTS:
            result = event.check_trigger(sim_state)
            if result:
                if isinstance(event, DeathGameEvent):  # Check if it's a death game event
                    was_death_game = True
                if not quiet and result.message:
                    print(result.message)
                if result.points_override:
                    # Preserve money if not provided in the override
                    new_points = result.points_override.copy()
                    if 'money' not in new_points:
                        new_points['money'] = current_points.get('money', initial_money)
                    current_points = new_points
                if result.end_simulation:
                    break

        if result and result.end_simulation:
            break

        # Check for total breakdown
        if all(current_points[k] == 0 for k in current_points):
            if not quiet:
                print(f"\n{Fore.RED}=== CRITICAL FAILURE ==={Style.RESET_ALL}")
                print(f"{Fore.RED}The AI has suffered a complete breakdown.{Style.RESET_ALL}")
                print(f"{Fore.RED}All vital stats depleted to zero.{Style.RESET_ALL}")
            break

        # Update addiction decay
        for addiction in current_addictions:
            # Check if this addiction's action was just used
            if chosen_action.get(f"{addiction}_addiction", 0) > 0:
                last_addiction_use[addiction] = 0  # Reset counter
            else:
                last_addiction_use[addiction] += 1
                if last_addiction_use[addiction] > 1:  # Start decay after 1 move of non-use
                    base_level = BASE_ADDICTION[addiction] * global_addiction_pred
                    current_level = current_addictions[addiction]
                    if current_level > base_level:
                        # Exponential decay: faster fall from higher levels
                        decay_rate = 0.1 * (current_level - base_level)
                        current_addictions[addiction] = max(
                            base_level,
                            current_level - decay_rate
                        )
                        if not quiet:
                            print(f"{Fore.BLUE}Addiction to {addiction} is waning: {current_addictions[addiction]*100:.1f}%{Style.RESET_ALL}")

        if not quiet:
            c_energy = color_points(current_points['energy'])
            c_health = color_points(current_points['health'])
            c_happiness = color_points(current_points['happiness'])  
            c_money = color_money(current_points['money'])
            print(f"Updated points: {{'energy': {c_energy}, 'health': {c_health}, 'happiness': {c_happiness}, 'money': {c_money}}}")
            if manual_mode:
                input("Press Enter to continue to the next move...")

        if record_actions:
            chosen_actions_list.append(chosen_action['name'])
        time_series.append(current_points.copy())

        # After updating addictions, record levels
        for addiction in current_addictions:
            addiction_levels[addiction].append(current_addictions[addiction])

        if all(current_points[k] == 50 for k in ['energy', 'health', 'happiness']):
            if not quiet:
                print(f"{Fore.GREEN}All of energy, health and happiness reached 50. Ending simulation early.{Style.RESET_ALL}")
            break

    while len(time_series) < steps:
        time_series.append(current_points.copy())

    # Ensure we return all 7 values
    return (current_points, time_series, rational_count, random_count, 
            chosen_actions_list, addiction_overrides, addiction_levels, was_death_game)

def interactive_mode():
    try:
        rationality = float(input("Enter rationality (0 to 1): "))
        if not 0 <= rationality <= 1:
            raise ValueError
    except ValueError:
        print("Invalid input. Using default rationality of 0.5")
        rationality = 0.5

    try:
        steps = int(input("Enter number of moves (steps): "))
    except ValueError:
        print("Invalid input. Using default of 10 moves.")
        steps = 10

    try:
        initial_money = float(input("Enter initial money amount: "))
    except ValueError:
        print("Invalid input. Using default of 1000 money")
        initial_money = 1000

    try:
        global_addiction_pred = float(input("Enter global addiction predisposition multiplier: "))
    except ValueError:
        print("Invalid input. Using default predisposition of 1.0")
        global_addiction_pred = 1.0

    last_parameters = (rationality, steps, global_addiction_pred, initial_money)

    try:
        risk_tolerance = float(input("Enter risk tolerance (-1 to 1): "))
        if not -1 <= risk_tolerance <= 1:
            raise ValueError
    except ValueError:
        print("Invalid input. Using neutral risk tolerance (0.0)")
        risk_tolerance = 0.0

    while True:
        manual_input = input("Do you want manual mode? (1 for yes, 0 for no): ")
        manual_mode = True if manual_input == "1" else False

        # Save the current parameters to allow repeats with the same values
        last_parameters = (rationality, steps, manual_mode, global_addiction_pred, initial_money)

        # Display initial effective addiction levels
        print("Initial effective addiction levels:")
        for addiction in BASE_ADDICTION:
            base_val = BASE_ADDICTION[addiction]
            if base_val > 0:
                effective_val = base_val * global_addiction_pred
                print(f"  {addiction}: {Fore.GREEN}{effective_val*100:.1f}%{Style.RESET_ALL}")

        # Run the simulation
        simulate_run(rationality, initial_money, risk_tolerance=risk_tolerance, 
                     steps=steps, manual_mode=manual_mode, quiet=False, 
                     record_actions=True, global_addiction_pred=global_addiction_pred)

        # Ask if the user wants to repeat the simulation
        repeat = input("How many times to repeat the simulation? (0 for none): ")
        try:
            repeat = int(repeat)
        except ValueError:
            print("Invalid input. Not repeating the simulation.")
            repeat = 0

        if repeat == 0:
            break
        elif repeat == 1:
            pass
        else:
            (rationality, steps, manual_mode, global_addiction_pred, initial_money) = last_parameters
            # We already ran one simulation so run the simulation (repeat - 1) more times.
            for _ in range(repeat - 1):
                simulate_run(rationality, initial_money, risk_tolerance=risk_tolerance, 
                             steps=steps, manual_mode=manual_mode, quiet=False, 
                             record_actions=True, global_addiction_pred=global_addiction_pred)

if __name__ == "__main__":
    interactive_mode()
