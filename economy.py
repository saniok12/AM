from typing import Dict, Union

# Constants
INITIAL_MONEY = 5000  # Starting amount
TARGET_MONEY = 5000   # Amount at which rational AI is satisfied
MONEY_WEIGHT = 0.4    # Base weight for money in decisions (less than health/energy importance)

def calculate_money_factor(current_money: float) -> float:
    """
    Calculate how much the AI should care about making more money.
    Returns a value between 0.1 and 1.0.
    """
    if current_money >= TARGET_MONEY:
        return 0.1  # Minimal interest in making more money
    
    # Linear decrease as money approaches target
    factor = 1.0 - (current_money / TARGET_MONEY) * 0.9
    return max(0.1, factor)

def compute_money_weight(action: Dict[str, Union[str, int, float]], current_money: float) -> float:
    """Calculate the weighted contribution of money to the decision."""
    money_change = action.get('money', 0)
    money_factor = calculate_money_factor(current_money)
    return money_factor * money_change * MONEY_WEIGHT