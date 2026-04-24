# core
from src.analysis.io.loader import DataLoader
from src.f036_interneuron_dynamics.analysis import analyze_interneuron_dynamics
from src.f036_interneuron_dynamics.plot import plot_interneuron_dynamics

def run_f036():
    print(f"""[action] Executing Module f036: Interneuron Dynamics...""")
    loader = DataLoader()
    
    # Analyze
    results = analyze_interneuron_dynamics(loader)
    
    # Plot
    output_dir = loader.get_output_dir("f036-interneuron-dynamics")
    plot_interneuron_dynamics(results, output_dir=output_dir)
    print(f"""[progress] Module f036 complete.""")

if __name__ == "__main__":
    run_f036()
