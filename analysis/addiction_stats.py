import numpy as np
from simulation import BASE_ADDICTION
from colorama import Fore, Style

def analyze_addiction_patterns(addiction_levels_list, chosen_actions_list):
    stats = {
        "override_frequencies": {},
        "addiction_progression": {},
        "addictive_action_counts": {},
        "max_addiction_levels": {},
        "recovery_rates": {},
        "avg_addiction_levels": {},
        "addiction_volatility": {},
        "consecutive_choices": {},
        "tolerance_zone_times": {},
        "longest_clean_streak": {},
        "relapse_count": {},
        "time_to_high_tolerance": {}
    }
    
    # Initialize tracking for each addiction type
    for addiction in BASE_ADDICTION:
        stats["override_frequencies"][addiction] = 0
        stats["addiction_progression"][addiction] = []
        stats["addictive_action_counts"][addiction] = 0
        stats["max_addiction_levels"][addiction] = 0
        stats["recovery_rates"][addiction] = 0
        stats["avg_addiction_levels"][addiction] = 0
        stats["addiction_volatility"][addiction] = 0
        stats["consecutive_choices"][addiction] = 0
        stats["tolerance_zone_times"][addiction] = {"low": 0, "medium": 0, "high": 0}
        stats["longest_clean_streak"][addiction] = 0
        stats["relapse_count"][addiction] = 0
        stats["time_to_high_tolerance"][addiction] = float('inf')
    
    total_steps = 0
    for levels in addiction_levels_list:
        # Safely get the length from one timeline, if available
        some_value = next(iter(levels.values())) if levels else []
        total_steps += len(some_value)
        for addiction in BASE_ADDICTION:
            if addiction in levels:
                timeline = levels[addiction]
                stats["addiction_progression"][addiction].extend(timeline)
                if timeline:  # Only update max if timeline is not empty
                    stats["max_addiction_levels"][addiction] = max(
                        stats["max_addiction_levels"][addiction],
                        max(timeline)
                    )
    
    # Count addictive actions using a mapping that links action names to addiction types
    addiction_action_map = {
        "drink": "alcohol",
        "gamble": "gambling",
        "shop": "shopping",
        "eat junk food": "junk_food"
    }
    
    for action in chosen_actions_list:
        act = action.lower()
        if act in addiction_action_map:
            addiction_type = addiction_action_map[act]
            stats["addictive_action_counts"][addiction_type] += 1

    # Calculate override frequencies if there were any addictive actions
    for addiction in BASE_ADDICTION:
        if stats["addictive_action_counts"][addiction] > 0:
            stats["override_frequencies"][addiction] = (
                stats["addictive_action_counts"][addiction] / total_steps
            )

    # Enhanced analysis: average levels and volatility
    for addiction in BASE_ADDICTION:
        timeline = stats["addiction_progression"][addiction]
        if timeline:
            stats["avg_addiction_levels"][addiction] = np.mean(timeline)
            stats["addiction_volatility"][addiction] = np.std(timeline)
            decreases = sum(1 for i in range(1, len(timeline))
                            if timeline[i] < timeline[i-1])
            stats["recovery_rates"][addiction] = decreases / len(timeline)
    
    # Enhanced timeline analysis: tolerance zones, clean streaks, and relapse counts
    for levels in addiction_levels_list:
        for addiction in BASE_ADDICTION:
            if addiction in levels:
                timeline = levels[addiction]
                current_clean_streak = 0
                last_level = 0
                was_decreasing = False
                
                for i, level in enumerate(timeline):
                    # Track tolerance zones based on level
                    if level > 0.7:
                        stats["tolerance_zone_times"][addiction]["high"] += 1
                    elif level > 0.4:
                        stats["tolerance_zone_times"][addiction]["medium"] += 1
                    else:
                        stats["tolerance_zone_times"][addiction]["low"] += 1
                    
                    # Track time to reach high tolerance
                    if level > 0.7 and stats["time_to_high_tolerance"][addiction] == float('inf'):
                        stats["time_to_high_tolerance"][addiction] = i
                    
                    # Track clean streaks and relapses
                    if level < last_level:
                        current_clean_streak += 1
                        was_decreasing = True
                    elif level > last_level:
                        if was_decreasing and (level > last_level + 0.05):
                            stats["relapse_count"][addiction] += 1
                            was_decreasing = False
                        if current_clean_streak > stats["longest_clean_streak"][addiction]:
                            stats["longest_clean_streak"][addiction] = current_clean_streak
                        current_clean_streak = 0
                    last_level = level

    return stats

def report_addiction_stats(stats):
    """Print formatted addiction statistics."""
    print(f"\n{Fore.CYAN}=== Addiction Analysis ==={Style.RESET_ALL}")
    
    for addiction in BASE_ADDICTION:
        if stats["max_addiction_levels"][addiction] > 0:
            print(f"\n{Fore.YELLOW}{addiction.capitalize()}{Style.RESET_ALL}:")
            print(f"  Peak addiction level: {stats['max_addiction_levels'][addiction]*100:.1f}%")
            print(f"  Average addiction level: {stats['avg_addiction_levels'][addiction]*100:.1f}%")
            print(f"  Addiction volatility: {stats['addiction_volatility'][addiction]*100:.1f}%")
            print(f"  Override frequency: {stats['override_frequencies'][addiction]*100:.1f}%")
            print(f"  Recovery rate: {stats['recovery_rates'][addiction]*100:.1f}%")
            print(f"  Addictive actions chosen: {stats['addictive_action_counts'][addiction]}")
            
            zones = stats["tolerance_zone_times"][addiction]
            total_time = sum(zones.values())
            print(f"\n  Tolerance Zone Distribution:")
            if total_time > 0:
                print(f"    Low (<40%): {zones['low']/total_time*100:.1f}% of time")
                print(f"    Medium (40-70%): {zones['medium']/total_time*100:.1f}% of time")
                print(f"    High (>70%): {zones['high']/total_time*100:.1f}% of time")
            else:
                print(f"    Low (<40%): 0.0% of time")
                print(f"    Medium (40-70%): 0.0% of time")
                print(f"    High (>70%): 0.0% of time")
            
            if stats["time_to_high_tolerance"][addiction] != float('inf'):
                print(f"  Time to reach high tolerance: {stats['time_to_high_tolerance'][addiction]} moves")
            
            print(f"  Longest clean streak: {stats['longest_clean_streak'][addiction]} moves")
            print(f"  Number of relapses: {stats['relapse_count'][addiction]}")