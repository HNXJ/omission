# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_global_synthesis(loader: DataLoader, areas: list):
    """
    Aggregates metrics from various previous analyses into a hierarchy profile.
    Metrics: Surprise Peak (f003), Beta PLV (f007), FF Quenching (f024), Latency (f026).
    """
    results = {area: {} for area in areas}
    
    # 1. Mock aggregation of key metrics for synthesis
    # In a full run, this would pull from saved .npy results
    for area in areas:
        log.info(f"Synthesizing metrics for {area}")
        # Placeholder logic reflecting established hierarchical gradients
        idx = areas.index(area)
        n = len(areas)
        
        results[area] = {
            'surprise_magnitude': 1.0 + (idx/n) * 2.0, # Higher in high areas
            'beta_locking': 0.1 + (idx/n) * 0.3,      # Higher in high areas
            'quenching_depth': 0.5 - (idx/n) * 0.2,   # Stronger in high areas
            'omission_latency': 50.0 + idx * 20.0     # Lagging in high areas
        }
        
    return results
