# analysis/action_stats.py
from collections import Counter
from colorama import Fore, Style
from actions import actions  # Import the full list of actions

def report_action_stats(all_chosen_actions):
    if not all_chosen_actions:
        print("No action data provided.")
        return

    counts = Counter(all_chosen_actions)
    most_common = counts.most_common()
    most_chosen_action, most_count = most_common[0]
    # For the least chosen, filter out actions that were never chosen, then find the minimum
    least_chosen_action, least_count = min(most_common, key=lambda x: x[1])
    
    # Create a mapping from action name to its award dictionary
    action_awards = {action['name']: action for action in actions}

    # Retrieve the award info for the most and least chosen actions
    most_awards = action_awards.get(most_chosen_action, {})
    least_awards = action_awards.get(least_chosen_action, {})

    def format_awards(award_dict):
        # Format the award info in the form "energy: +10, health: +5, happiness: -3"
        return ", ".join([f"{key}: {award_dict.get(key, 0):+d}" for key in ['energy','health','happiness']])
    
    print(f"{Fore.CYAN}Most chosen action:{Style.RESET_ALL} {most_chosen_action} ({most_count} times) Awards: {format_awards(most_awards)}")
    print(f"{Fore.CYAN}Least chosen action:{Style.RESET_ALL} {least_chosen_action} ({least_count} times) Awards: {format_awards(least_awards)}")
