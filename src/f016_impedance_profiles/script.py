# beta
from src.f016_impedance_profiles.analysis import analyze_impedance
from src.f016_impedance_profiles.plot import plot_impedance

def run_f016():
    results = analyze_impedance(session="230629", probe=0)
    if results:
        plot_impedance(results)

if __name__ == "__main__":
    run_f016()
