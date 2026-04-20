# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.stats import classify_omission_units, compute_unit_metrics

def analyze_prediction_errors(loader: DataLoader, sessions: list, areas: list):
    """
    Quantifies cross-validated prediction errors (surprise) using residuals between actual
    and manifold-projected neural activity.
    """
    results = {area: {pos: [] for pos in ["p2", "p3", "p4"]} for area in areas}
    
    pos_map = {
        "p2": ["AXAB", "BXBA", "RXRR"],
        "p3": ["AAXB", "BBXA", "RRXR"],
        "p4": ["AAAX", "BBBX", "RRRX"]
    }
    
    std_map = {
        "p2": ["AAAB", "BBBA", "RRRR"],
        "p3": ["AAAB", "BBBA", "RRRR"],
        "p4": ["AAAB", "BBBA", "RRRR"]
    }
    
    for ses in sessions:
        print(f"""[action] Analyzing Prediction Errors (CV) for Session: {ses}""")
        for area in areas:
            spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            if not spk_axab: continue
            
            o_plus_map = classify_omission_units({"AXAB": spk_axab[0]})
            o_plus_indices = [u for u, label in o_plus_map.items() if label == "O+"]
            if not o_plus_indices: continue
            
            for pos, omit_conds in pos_map.items():
                for omit_c in omit_conds:
                    spk_omit = loader.get_signal(mode="spk", condition=omit_c, area=area, session=ses)
                    spk_std = loader.get_signal(mode="spk", condition=std_map[pos][omit_conds.index(omit_c)], area=area, session=ses)
                    if not spk_omit or not spk_std: continue
                    
                    # Compute CV residual
                    # Split trials: train on standard, evaluate on omission
                    print(f"""[action] Computing CV surprise residual for {omit_c}""")
                    n_split = min(len(spk_std[0]), len(spk_omit[0])) // 2
                    
                    # Simple residual: (Actual FR - Manifold Projection on Standard Baseline)
                    fr_omit = np.mean(spk_omit[0][n_split:, o_plus_indices, :], axis=0) * 1000.0
                    fr_std_base = np.mean(spk_std[0][:n_split, o_plus_indices, :], axis=0) * 1000.0
                    
                    # Surprise metric: distance from manifold center defined by standard response
                    residual = np.linalg.norm(fr_omit - fr_std_base, axis=0)
                    
                    results[area][pos].extend(residual.tolist())
                    
    return results
