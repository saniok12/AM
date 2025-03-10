import matplotlib.pyplot as plt

def plot_histograms(simulation_results):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, (key, values) in enumerate(simulation_results.items()):
        axes[idx].hist(values, bins=10, edgecolor='black')
        axes[idx].set_title(f"Histogram of final {key} values")
        axes[idx].set_xlabel(f"{key.capitalize()} points")
        axes[idx].set_ylabel("Frequency")
    plt.tight_layout()
    plt.show(block=False)

def plot_evolution(avg_evolution, steps, rationality):
    plt.figure(figsize=(10, 6))
    moves_range = range(1, steps + 1)
    plt.plot(moves_range, avg_evolution['energy'], marker='o', label='Energy')
    plt.plot(moves_range, avg_evolution['health'], marker='o', label='Health')
    plt.plot(moves_range, avg_evolution['happiness'], marker='o', label='Happiness')
    plt.xlabel("Move")
    plt.ylabel("Average Points")
    plt.title(f"Average Evolution over Simulations (Rationality = {rationality})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=False)
