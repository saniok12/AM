from typing import Dict, Union
from colorama import Fore, Style

# Constants
TARGET_MONEY = 5000   # Amount at which rational AI is satisfied
MONEY_WEIGHT = 0.4    # Base weight for money in decisions

def color_money(amount: float) -> str:
    """Color-code money amount based on thresholds"""
    if amount >= 5000:
        return f"{Fore.GREEN}Ƶ{amount:.0f}{Style.RESET_ALL}"
    elif amount >= 1000:
        return f"{Fore.YELLOW}Ƶ{amount:.0f}{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}Ƶ{amount:.0f}{Style.RESET_ALL}"

def calculate_money_factor(current_money: float) -> float:
    """Calculate how much the AI should care about making more money."""
    if current_money >= TARGET_MONEY:
        return 0.1
    factor = 1.0 - (current_money / TARGET_MONEY) * 0.9
    return max(0.1, factor)

def compute_money_weight(action: Dict[str, Union[str, int, float]], current_money: float) -> float:
    """Calculate the weighted contribution of money to the decision."""
    money_change = action.get('money', 0)
    money_factor = calculate_money_factor(current_money)
    return money_factor * money_change * MONEY_WEIGHT