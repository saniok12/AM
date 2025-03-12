import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore, Style
from simulation import simulate_run

def rationality_sweep_mode(default_simulations=None, steps=10):
    if default_simulations is None:
        try:
            num_simulations = int(input("Enter number of simulations for each rationality value: "))
        except ValueError:
            print("Invalid input. Using 10 simulations.")
            num_simulations = 10
    else:
        num_simulations = default_simulations

    sweep_increment = 0.05
    rationality_values = [round(x, 2) for x in np.arange(0.0, 1.0 + sweep_increment, sweep_increment)]
    
    energy_averages = []
    health_averages = []
    happiness_averages = []

    try:
        risk_tolerance = float(input("Enter risk tolerance (-1 to 1): "))
        if not -1 <= risk_tolerance <= 1:
            raise ValueError
    except ValueError:
        print("Invalid input. Using neutral risk tolerance (0.0)")
        risk_tolerance = 0.0

    print(f"{Fore.GREEN}Sweeping through rationality values...{Style.RESET_ALL}")
    for r in rationality_values:
        total_energy, total_health, total_happiness = 0, 0, 0
        for _ in range(num_simulations):
            final_points, _, _, _, _, _, _, _ = simulate_run(
                r, 
                risk_tolerance=risk_tolerance,
                steps=steps, 
                manual_mode=False, 
                quiet=True
            )
            total_energy += final_points["energy"]
            total_health += final_points["health"]
            total_happiness += final_points["happiness"]
        avg_energy = total_energy / num_simulations
        avg_health = total_health / num_simulations
        avg_happiness = total_happiness / num_simulations
        
        energy_averages.append(avg_energy)
        health_averages.append(avg_health)
        happiness_averages.append(avg_happiness)
        print(
            f"{Fore.CYAN}Rationality {r}:{Style.RESET_ALL} "
            f"Energy: {Fore.YELLOW}{avg_energy:.2f}{Style.RESET_ALL}, "
            f"Health: {Fore.YELLOW}{avg_health:.2f}{Style.RESET_ALL}, "
            f"Happiness: {Fore.YELLOW}{avg_happiness:.2f}{Style.RESET_ALL}"
        )

    plt.figure(figsize=(10, 6))
    plt.plot(rationality_values, energy_averages, marker='o', label="Energy")
    plt.plot(rationality_values, health_averages, marker='o', label="Health")
    plt.plot(rationality_values, happiness_averages, marker='o', label="Happiness")
    plt.xlabel("Rationality")
    plt.ylabel("Average Final Points")
    plt.title("Average Final Points vs. Rationality")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    rerun = input(f"\n{Fore.CYAN}Do you want to run another rationality sweep? (1 for yes, 0 for no): {Style.RESET_ALL}")
    if rerun == "1":
        rationality_sweep_mode(default_simulations=num_simulations, steps=steps)
