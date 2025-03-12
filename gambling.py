from dataclasses import dataclass
import random
from colorama import Fore, Style

@dataclass
class BetProfile:
    min_chance: float
    max_chance: float
    min_payout: float
    max_payout: float
    min_bet_pct: float
    max_bet_pct: float
    description: str

GAMBLING_PROFILES = {
    "low_risk": BetProfile(
        0.60, 0.75, 1.2, 1.5, 0.02, 0.10,
        "Conservative bet with high chance of small win"
    ),
    "medium_risk": BetProfile(
        0.25, 0.40, 2.0, 3.0, 0.10, 0.30,
        "Balanced bet with moderate risk and reward"
    ),
    "high_risk": BetProfile(
        0.05, 0.15, 5.0, 10.0, 0.30, 0.90,
        "Aggressive bet with high potential payout"
    )
}

def choose_gambling_profile(risk_tolerance: float, addiction_level: float) -> str:
    """Select betting profile based on risk tolerance and addiction level"""
    # Addiction makes you take bigger risks
    effective_risk = min(1.0, risk_tolerance + (addiction_level * 0.5))
    
    if effective_risk < -0.3:
        return "low_risk"
    elif effective_risk < 0.3:
        return "medium_risk"
    else:
        return "high_risk"

def calculate_bet_parameters(profile_name: str, risk_tolerance: float, 
                           addiction_level: float, current_money: float):
    """Calculate specific betting parameters within the chosen profile"""
    profile = GAMBLING_PROFILES[profile_name]
    
    # Convert risk_tolerance from [-1,1] to [0,1] for interpolation
    risk_factor = (risk_tolerance + 1) / 2
    
    # Interpolate within profile ranges
    win_chance = profile.min_chance + (profile.max_chance - profile.min_chance) * (1 - risk_factor)
    payout = profile.min_payout + (profile.max_payout - profile.min_payout) * risk_factor
    
    # Bet percentage influenced by both risk and addiction
    base_bet_pct = profile.min_bet_pct + (profile.max_bet_pct - profile.min_bet_pct) * risk_factor
    # Addiction increases bet size
    final_bet_pct = min(1.0, base_bet_pct * (1 + addiction_level))
    
    bet_amount = round(current_money * final_bet_pct / 10) * 10  # Round to nearest 10
    
    return win_chance, payout, bet_amount

def execute_gambling(current_points: dict, risk_tolerance: float, 
                    addiction_level: float, quiet: bool = False) -> dict:
    """Execute a gambling action and return the results"""
    
    current_money = current_points['money']
    
    # Choose gambling profile
    profile_name = choose_gambling_profile(risk_tolerance, addiction_level)
    win_chance, payout, bet = calculate_bet_parameters(
        profile_name, risk_tolerance, addiction_level, current_money
    )
    
    if not quiet:
        print(f"\n{Fore.YELLOW}Gambling Profile: {profile_name.replace('_', ' ').title()}{Style.RESET_ALL}")
        print(f"Win Chance: {win_chance*100:.1f}%")
        print(f"Payout: {payout:.1f}x")
        print(f"Bet Amount: Ƶ{bet}")
    
    # Execute the bet
    if random.random() < win_chance:
        winnings = int(bet * payout)
        money_change = winnings - bet
        if not quiet:
            print(f"{Fore.GREEN}Won Ƶ{winnings}! (Net: +Ƶ{money_change}){Style.RESET_ALL}")
    else:
        money_change = -bet
        if not quiet:
            print(f"{Fore.RED}Lost Ƶ{bet}{Style.RESET_ALL}")
    
    # Update and return new points
    result = current_points.copy()
    result['money'] += money_change
    result['energy'] -= 2  # Base energy cost
    result['happiness'] += 6 if money_change > 0 else -2  # Happiness impact
    
    return result