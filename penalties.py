from colorama import Fore, Style
from config import GAME_CONFIG

def calculate_breakdown_penalty(turns_at_zero):
    """Calculate exponentially increasing happiness penalty."""
    return min(GAME_CONFIG['STATS']['MAX_VALUE'], 
              GAME_CONFIG['BREAKDOWN']['BASE_PENALTY'] * 
              (GAME_CONFIG['BREAKDOWN']['MULTIPLIER'] ** (turns_at_zero - 1)))

def check_and_apply_penalties(current_points: dict, zero_stat_turns: dict, quiet: bool = False) -> dict:
    """Check each stat and apply penalties if at zero."""
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