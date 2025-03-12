import statistics
import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style
init()
from simulation import simulate_run, BASE_ADDICTION
from analysis.plotting import plot_histograms, plot_evolution
from analysis.action_stats import report_action_stats
from analysis.addiction_stats import analyze_addiction_patterns, report_addiction_stats

def data_collection_mode():
    while True:
        try:
            num_simulations = int(input("Enter number of simulations: "))
        except ValueError:
            print("Invalid input. Using 10 simulations.")
            num_simulations = 10

        try:
            steps = int(input("Enter number of moves (steps) for each simulation: "))
        except ValueError:
            print("Invalid input. Using default of 10 moves.")
            steps = 10

        try:
            global_addiction_pred = float(input("Enter global addiction predisposition multiplier: "))
        except ValueError:
            print("Invalid input. Using default predisposition of 1.0")
            global_addiction_pred = 1.0

        # Display initial effective addiction levels
        print("Initial effective addiction levels:")
        for addiction in BASE_ADDICTION:
            base_val = BASE_ADDICTION[addiction]
            if base_val > 0:
                effective_val = base_val * global_addiction_pred
                print(f"  {addiction}: {Fore.GREEN}{effective_val*100:.1f}%{Style.RESET_ALL}")

        rationality_input = input("Enter rationality (0 to 1) or type 'sweep' for a rationality sweep: ").strip().lower()
        if (rationality_input == "sweep"):
            from analysis.rationality_sweep import rationality_sweep_mode
            rationality_sweep_mode(default_simulations=num_simulations, steps=steps)
            rerun = input(f"\n{Fore.CYAN}Do you want to run another data collection? (1 for yes, 0 for no): {Style.RESET_ALL}")
            if rerun != "1":
                break
            continue

        try:
            rationality = float(rationality_input)
            if not 0 <= rationality <= 1:
                raise ValueError
        except ValueError:
            print("Invalid input. Using default rationality of 0.5")
            rationality = 0.5

        # Initialize data collection structures
        all_final_points = []
        all_time_series = []
        all_addiction_overrides = []
        all_addiction_levels = []
        chosen_actions = []
        total_rational = 0
        total_random = 0
        simulation_results = {
            'energy': [],
            'health': [], 
            'happiness': [], 
            'money': []
        }
        evolution = {
            'energy': [0] * steps,
            'health': [0] * steps,
            'happiness': [0] * steps,
            'money': [0] * steps  # Add money to evolution tracking
        }

        # Initialize tolerance tracking across simulations
        tolerance_stats = {addiction: {'low': 0, 'medium': 0, 'high': 0} for addiction in BASE_ADDICTION}
        fastest_high_tolerance = {addiction: float('inf') for addiction in BASE_ADDICTION}
        longest_clean_streaks = {addiction: 0 for addiction in BASE_ADDICTION}
        total_relapses = {addiction: 0 for addiction in BASE_ADDICTION}
        
        # Add breakdown tracking
        total_breakdowns = 0
        breakdown_causes = {'energy_health': 0, 'cascade': 0}
        survival_times = []

        # Add death game tracking
        death_game_stats = {
            'total': 0,
            'wins': 0,
            'losses': 0
        }

        # Modify breakdown tracking with an extra category
        breakdown_causes = {
            'energy_health': 0,
            'cascade': 0,
            'death_game': 0
        }

        # Add stats configuration
        print("\nSelect statistics to display:")
        stats_config = {
            'basic': input("Show basic stats (final points, decisions)? (1/0): ") == "1",
            'breakdowns': input("Show breakdown analysis? (1/0): ") == "1",
            'addiction': input("Show addiction analysis? (1/0): ") == "1",
            'tolerance': input("Show tolerance zones? (1/0): ") == "1",
            'plots': input("Generate plots? (1/0): ") == "1"
        }

        # Run simulations once and collect all data
        initial_money = float(input("Enter initial money amount: "))
        for _ in range(num_simulations):
            result = simulate_run(
                rationality,
                initial_money,  # Pass initial_money here
                steps=steps,
                manual_mode=False,
                quiet=True,
                record_actions=True,
                global_addiction_pred=global_addiction_pred
            )
            
            final_points, time_series, rat_count, rand_count, actions, overrides, levels, was_death_game = result
            
            # Process death game results
            if was_death_game:
                death_game_stats['total'] += 1
                if all(final_points[k] == 50 for k in ['energy', 'health', 'happiness']):  # Check only vital stats
                    death_game_stats['wins'] += 1
                else:
                    death_game_stats['losses'] += 1

            # Check for breakdowns based on vital stats only (excluding money)
            if all(final_points[k] == 0 for k in ['energy', 'health', 'happiness']):
                total_breakdowns += 1
                survival_times.append(len(time_series))
                
                if was_death_game:
                    breakdown_causes['death_game'] += 1
                elif len(time_series) > 1:
                    previous_state = time_series[-2]
                    if previous_state['energy'] == 0 and previous_state['health'] == 0:
                        breakdown_causes['energy_health'] += 1
                    else:
                        breakdown_causes['cascade'] += 1

            # Collect all simulation data
            all_final_points.append(final_points)
            all_time_series.append(time_series)
            all_addiction_overrides.append(overrides)
            all_addiction_levels.append(levels)
            chosen_actions.extend(actions if actions else [])
            
            # Track rational/random decisions
            total_rational += rat_count
            total_random += rand_count
            
            # Collect data for plotting
            for key in simulation_results:
                simulation_results[key].append(final_points[key])
            
            # Sum up evolution data
            for i, points_dict in enumerate(time_series):
                evolution['energy'][i] += points_dict['energy']
                evolution['health'][i] += points_dict['health']
                evolution['happiness'][i] += points_dict['happiness']
                evolution['money'][i] += points_dict['money']  # Add money evolution

            # Track tolerance zones across all simulations
            for addiction, timeline in levels.items():
                for level in timeline:
                    if level > 0.7:
                        tolerance_stats[addiction]['high'] += 1
                    elif level > 0.4:
                        tolerance_stats[addiction]['medium'] += 1
                    else:
                        tolerance_stats[addiction]['low'] += 1
                
                try:
                    high_tolerance_time = next(i for i, level in enumerate(timeline) if level > 0.7)
                    fastest_high_tolerance[addiction] = min(fastest_high_tolerance[addiction], high_tolerance_time)
                except StopIteration:
                    pass

        # Calculate statistics
        stats = {}
        for key, values in simulation_results.items():
            avg = statistics.mean(values)
            stats[key] = {
                'average': avg,
                'min': min(values),
                'max': max(values),
                'variance': statistics.pvariance(values),
                'std_dev': statistics.pstdev(values),
                'median': statistics.median(values)
            }

        # Add money-related statistics
        money_changes = [final_points['money'] - initial_money for final_points in all_final_points]
        avg_money_change = statistics.mean(money_changes)

        if stats_config['basic']:
            print(f"\n{Fore.CYAN}After {num_simulations} simulations, statistics for final points:{Style.RESET_ALL}")
            for key in stats:
                print(
                    f"{Fore.YELLOW}{key.capitalize()}{Style.RESET_ALL}: "
                    f"Average = {Fore.GREEN}{stats[key]['average']:.2f}{Style.RESET_ALL}, "
                    f"Min = {Fore.RED}{stats[key]['min']}{Style.RESET_ALL}, "
                    f"Max = {Fore.GREEN}{stats[key]['max']}{Style.RESET_ALL}, "
                    f"Variance = {stats[key]['variance']:.2f}, "
                    f"Std Dev = {stats[key]['std_dev']:.2f}, "
                    f"Median = {stats[key]['median']}"
                )
            print(f"\n{Fore.GREEN}Average money change: {avg_money_change:.2f}{Style.RESET_ALL}")

            print(f"\n{Fore.MAGENTA}Total rational decisions:{Style.RESET_ALL} {total_rational}")
            print(f"{Fore.MAGENTA}Total random decisions:{Style.RESET_ALL} {total_random}")

        if stats_config['breakdowns']:
            print(f"\n{Fore.RED}=== Breakdown Analysis ==={Style.RESET_ALL}")
            print(f"Total breakdowns: {total_breakdowns} ({(total_breakdowns/num_simulations)*100:.1f}% of simulations)")
            if total_breakdowns > 0:
                print(f"Average survival time: {sum(survival_times)/len(survival_times):.1f} moves")
                print("\nBreakdown causes:")
                print(f"  Death Games: {breakdown_causes['death_game']} ({(breakdown_causes['death_game']/total_breakdowns)*100:.1f}%)")
                print(f"  Physical depletion: {breakdown_causes['energy_health']} ({(breakdown_causes['energy_health']/total_breakdowns)*100:.1f}%)")
                print(f"  Cascading failure: {breakdown_causes['cascade']} ({(breakdown_causes['cascade']/total_breakdowns)*100:.1f}%)")
            
            print(f"\n{Fore.YELLOW}Death Game Statistics:{Style.RESET_ALL}")
            print(f"Total Death Games: {death_game_stats['total']}")
            if death_game_stats['total'] > 0:
                win_rate = (death_game_stats['wins'] / death_game_stats['total']) * 100
                print(f"  Wins: {death_game_stats['wins']} ({win_rate:.1f}%)")
                print(f"  Losses: {death_game_stats['losses']} ({100-win_rate:.1f}%)")

        if stats_config['tolerance']:
            print(f"\n{Fore.CYAN}=== Addiction Tolerance Analysis ==={Style.RESET_ALL}")
            for addiction in BASE_ADDICTION:
                total_time = sum(tolerance_stats[addiction].values())
                if total_time > 0:
                    print(f"\n{Fore.YELLOW}{addiction.capitalize()}{Style.RESET_ALL}:")
                    print("Time spent in tolerance zones:")
                    for zone, time in tolerance_stats[addiction].items():
                        percentage = (time / total_time) * 100
                        print(f"  {zone.capitalize()}: {percentage:.1f}%")

        if stats_config['plots']:
            report_action_stats(chosen_actions)
            plot_histograms(simulation_results)
            avg_evolution = {'energy': [], 'health': [], 'happiness': []}
            for i in range(steps):  # Changed from 'moves' to 'steps'
                avg_evolution['energy'].append(evolution['energy'][i] / num_simulations)
                avg_evolution['health'].append(evolution['health'][i] / num_simulations)
                avg_evolution['happiness'].append(evolution['happiness'][i] / num_simulations)
                avg_evolution['money'].append(evolution['money'][i] / num_simulations)  # Add money evolution
            plot_evolution(avg_evolution, steps, rationality)  # Changed from 'moves' to 'steps'

        if stats_config['addiction']:
            addiction_stats = analyze_addiction_patterns(all_addiction_levels, chosen_actions)
            report_addiction_stats(addiction_stats)

        rerun = input(f"\n{Fore.CYAN}Do you want to run another data collection? (1 for yes, 0 for no): {Style.RESET_ALL}")
        if rerun != "1":
            break

if __name__ == "__main__":
    data_collection_mode()
