from colorama import Fore, Style
from typing import Dict, List
from economy import color_money

def color_points(value: float) -> str:
    """Color the numeric points based on thresholds."""
    if value < 10:
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    elif value < 35:
        return f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
    else:
        return f"{Fore.GREEN}{value}{Style.RESET_ALL}"

def color_cost(amount: float) -> str:
    """Color the cost in brackets: positive in green, negative in red, zero in default."""
    if amount > 0:
        return f"{Fore.GREEN}+{amount}{Style.RESET_ALL}"
    elif amount < 0:
        return f"{Fore.RED}{amount}{Style.RESET_ALL}"
    else:
        return f"{amount}"

def format_action_display(action: Dict, weighted_score: float) -> str:
    """Format a single action for display"""
    name = action['name']
    effects = []
    
    for stat in ['energy', 'health', 'happiness']:
        if stat in action:
            effects.append(f"{stat}: {color_cost(action[stat])}")
    
    if 'money' in action:
        effects.append(f"money: {color_cost(action['money'])}")
        
    effects_str = ", ".join(effects)
    return f"{name} [{effects_str}] (Score: {weighted_score:.2f})"

def show_stats(current_points: Dict[str, float], quiet: bool = False) -> None:
    """Display current stats"""
    if quiet:
        return
        
    print("\nCurrent stats:")
    stats_display = []
    
    # Display vital stats first
    for stat in ['energy', 'health', 'happiness']:
        if stat in current_points:
            stats_display.append(f"{stat}: {color_points(current_points[stat])}")
    
    # Display money if present
    if 'money' in current_points:
        stats_display.append(f"money: {color_money(current_points['money'])}")
    
    print(", ".join(stats_display))