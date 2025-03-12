from dataclasses import dataclass
import random
from colorama import Fore, Style
from utils import clamp  # Add this import

MAX_DEBT = 50000
LOAN_SHARK_RATES = {
    "small": {"amount": 1000, "turns": 5, "interest": 1.5},
    "medium": {"amount": 5000, "turns": 4, "interest": 2.0},
    "large": {"amount": 10000, "turns": 3, "interest": 2.5},
    "desperate": {"amount": 25000, "turns": 2, "interest": 3.0},
    "final": {"amount": 50000, "turns": 1, "interest": 4.0}
}

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
    payout = profile.min_payout + (profile.max_payout - profile.max_payout) * risk_factor
    
    # Bet percentage influenced by both risk and addiction
    base_bet_pct = profile.min_bet_pct + (profile.max_bet_pct - profile.max_bet_pct) * risk_factor
    # Addiction increases bet size
    final_bet_pct = min(1.0, base_bet_pct * (1 + addiction_level))
    
    bet_amount = round(current_money * final_bet_pct / 10) * 10  # Round to nearest 10
    
    return win_chance, payout, bet_amount

class DebtCollector:
    def __init__(self):
        self.active_loans = []  # List of (amount, turns_left, total_to_repay)
        self.total_debt = 0
        self.loan_count = 0

    def get_loan(self, risk_tolerance: float) -> tuple[float, str]:
        """Get a loan based on risk tolerance and previous loans"""
        if self.total_debt >= MAX_DEBT:
            return (0, f"{Fore.RED}💀 The debt collectors have made the AI disappear...{Style.RESET_ALL}")
            
        # Higher risk tolerance and more loans = bigger loans
        risk_factor = (risk_tolerance + 1) / 2  # Convert to 0-1
        desperation = min(1.0, self.loan_count * 0.25)  # Increases with each loan
        
        if desperation > 0.8 or risk_factor > 0.8:
            loan_type = "final"
        elif desperation > 0.6 or risk_factor > 0.6:
            loan_type = "desperate"
        elif desperation > 0.4 or risk_factor > 0.4:
            loan_type = "large"
        elif desperation > 0.2 or risk_factor > 0.2:
            loan_type = "medium"
        else:
            loan_type = "small"
            
        loan = LOAN_SHARK_RATES[loan_type]
        amount = loan["amount"]
        turns = loan["turns"]
        interest = loan["interest"]
        total_to_repay = amount * interest
        
        self.active_loans.append((amount, turns, total_to_repay))
        self.total_debt += total_to_repay
        self.loan_count += 1
        
        messages = {
            "small": f"{Fore.YELLOW}🦈 A shady figure offers a modest loan of Ƶ{amount} at {interest}x interest, to be repaid in {turns} turns (Total to repay: Ƶ{total_to_repay})...{Style.RESET_ALL}",
            "medium": f"{Fore.YELLOW}🦈 The loan shark grins as they hand over Ƶ{amount} at {interest}x interest, repayable in {turns} turns (Total to repay: Ƶ{total_to_repay})...{Style.RESET_ALL}",
            "large": f"{Fore.RED}🦈 Desperate times call for drastic measures... Borrowing Ƶ{amount} at {interest}x interest, to be repaid in {turns} turns (Total to repay: Ƶ{total_to_repay}) from dangerous people...{Style.RESET_ALL}",
            "desperate": f"{Fore.RED}☠️ The AI signs away its future for a massive loan of Ƶ{amount} at {interest}x interest, due in {turns} turns (Total to repay: Ƶ{total_to_repay})...{Style.RESET_ALL}",
            "final": f"{Fore.RED}💀 ONE FINAL DESPERATE LOAN OF Ƶ{amount} at {interest}x interest, repayable in {turns} turn{'s' if turns > 1 else ''} (Total to repay: Ƶ{total_to_repay})!!!{Style.RESET_ALL}"
        }
        
        return amount, messages[loan_type]

    def update_loans(self, current_money: float) -> tuple[float, str]:
        """Update loan timers and collect debts. Returns (money_change, message)"""
        if not self.active_loans:
            return (0, "")
            
        money_change = 0
        messages = []
        new_loans = []
        
        for amount, turns, to_repay in self.active_loans:
            if turns <= 1:
                # Always subtract the repayment amount
                money_change -= to_repay
                if current_money >= to_repay:
                    messages.append(f"{Fore.GREEN}Paid back Ƶ{to_repay} loan!{Style.RESET_ALL}")
                    self.total_debt -= to_repay  # Reduce total debt when paid
                    self.loan_count = max(0, self.loan_count - 1)  # Reduce loan count but not below 0
                else:
                    messages.append(
                        f"{Fore.RED}Failed to repay Ƶ{to_repay}! "
                        f"The debt collectors take everything...{Style.RESET_ALL}"
                    )
            else:
                new_loans.append((amount, turns - 1, to_repay))
                messages.append(
                    f"{Fore.YELLOW}Ƶ{to_repay} due in {turns-1} turns!{Style.RESET_ALL}"
                )
                
        self.active_loans = new_loans
        return money_change, "\n".join(messages)

def execute_gambling(current_points: dict, risk_tolerance: float, 
                    addiction_level: float, quiet: bool = False) -> dict:
    """Execute a gambling action and return the results"""
    # Add debt collector as a module-level variable
    global debt_collector
    if not hasattr(execute_gambling, 'debt_collector'):
        execute_gambling.debt_collector = DebtCollector()
    
    current_money = current_points['money']
    
    # If broke, try to borrow money
    if current_money == 0:
        loan_amount, message = execute_gambling.debt_collector.get_loan(risk_tolerance)
        if loan_amount == 0:  # Game over due to max debt
            return {
                'energy': 0,
                'health': 0,
                'happiness': 0,
                'money': 0
            }
        if not quiet:
            print(message)
        current_money = loan_amount
    
    # Choose gambling profile
    profile_name = choose_gambling_profile(risk_tolerance, addiction_level)
    win_chance, payout, bet = calculate_bet_parameters(
        profile_name, risk_tolerance, addiction_level, current_money
    )
    
    if not quiet:
        # More dramatic profile announcements
        profile_descriptions = {
            "low_risk": f"{Fore.CYAN}Playing it safe with a conservative bet...{Style.RESET_ALL}",
            "medium_risk": f"{Fore.YELLOW}Taking a calculated risk with a balanced bet...{Style.RESET_ALL}",
            "high_risk": f"{Fore.RED}Going all in with a high-stakes gamble!{Style.RESET_ALL}"
        }
        
        # Show current total debt if any exists
        if execute_gambling.debt_collector.total_debt > 0:
            print(f"{Fore.RED}Current total debt: Ƶ{execute_gambling.debt_collector.total_debt}{Style.RESET_ALL}")
            
        print(f"\n{profile_descriptions[profile_name]}")
        print(f"Win Chance: {win_chance*100:.1f}%")
        print(f"Payout: {payout:.1f}x")
        print(f"Bet Amount: Ƶ{bet}")
    
    # Execute the bet with more dramatic outcomes
    if random.random() < win_chance:
        winnings = int(bet * payout)
        money_change = winnings - bet
        # Scale stat boosts based on risk profile
        if profile_name == "high_risk":
            energy_boost = 10
            happiness_boost = 15
            win_message = f"{Fore.GREEN}JACKPOT! The risky bet pays off big time! +Ƶ{money_change}!{Style.RESET_ALL}"
        elif profile_name == "medium_risk":
            energy_boost = 6
            happiness_boost = 10
            win_message = f"{Fore.GREEN}Success! A nice win of Ƶ{winnings}! (Net: +Ƶ{money_change}){Style.RESET_ALL}"
        else:
            energy_boost = 3
            happiness_boost = 5
            win_message = f"{Fore.GREEN}A safe bet brings a steady profit of Ƶ{winnings}! (Net: +Ƶ{money_change}){Style.RESET_ALL}"
        
        if not quiet:
            print(win_message)
    else:
        money_change = -bet
        if not quiet:
            if profile_name == "high_risk":
                print(f"{Fore.RED}Disaster! The high-stakes gamble backfires! Lost Ƶ{bet}!{Style.RESET_ALL}")
            elif profile_name == "medium_risk":
                print(f"{Fore.RED}The risk didn't pay off. Lost Ƶ{bet}.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Even the safe bet didn't work out. Lost Ƶ{bet}.{Style.RESET_ALL}")
        energy_boost = 0
        happiness_boost = -2  # Keep existing happiness penalty for losses
    
    # Update and return new points with clamping
    result = current_points.copy()
    result['money'] = max(0, result['money'] + money_change)  # Prevent negative money
    
    # Use the base energy value from actions.py (2) plus any boost from winning
    base_energy = 0  # This matches the value in actions.py
    result['energy'] = clamp(result['energy'] + base_energy + energy_boost)  # Changed from -2 to +base_energy
    result['happiness'] = clamp(result['happiness'] + happiness_boost)
    
    # Before returning, update loans
    debt_change, debt_message = execute_gambling.debt_collector.update_loans(result['money'])
    if not quiet and debt_message:
        print(debt_message)
    result['money'] = max(0, result['money'] + debt_change)  
    
    # After debt message but before returning
    if not quiet and execute_gambling.debt_collector.total_debt > 0:
        print(f"{Fore.RED}Remaining total debt: Ƶ{execute_gambling.debt_collector.total_debt}{Style.RESET_ALL}")
    
    return result