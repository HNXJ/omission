# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.stats import classify_omission_units, compute_unit_metrics

def analyze_prediction_errors(loader: DataLoader, sessions: list, areas: list):
    """
    Quantifies the surprise transient (Prediction Error) across sequence positions (P2, P3, P4).
    Returns: {area: {pos: [transient_values]}}
    """
    results = {area: {pos: [] for pos in ["p2", "p3", "p4"]} for area in areas}
    
    # Omission conditions corresponding to sequence positions
    pos_map = {
        "p2": ["AXAB", "BXBA", "RXRR"],
        "p3": ["AAXB", "BBXA", "RRXR"],
        "p4": ["AAAX", "BBBX", "RRRX"]
    }
    
    # Standard conditions for contrast
    std_map = {
        "p2": ["AAAB", "BBBA", "RRRR"],
        "p3": ["AAAB", "BBBA", "RRRR"],
        "p4": ["AAAB", "BBBA", "RRRR"]
    }
    
    for ses in sessions:
        log.info(f"Analyzing Prediction Errors for Session: {ses}")
        for area in areas:
            # Load O+ units for this session/area
            # We classify based on AXAB (p2 omission) as the anchor
            spk_axab = loader.get_signal(mode="spk", condition="AXAB", area=area, session=ses)
            if not spk_axab: continue
            
            o_plus_map = classify_omission_units({"AXAB": spk_axab[0]})
            o_plus_indices = [u for u, label in o_plus_map.items() if label == "O+"]
            
            if not o_plus_indices: continue
            log.info(f"Found {len(o_plus_indices)} O+ units in {area} ({ses})")
            
            for pos, omit_conds in pos_map.items():
                for omit_c in omit_conds:
                    spk_omit = loader.get_signal(mode="spk", condition=omit_c, area=area, session=ses)
                    if not spk_omit: continue
                    
                    # Contrast with standard
                    std_c = std_map[pos][omit_conds.index(omit_c)]
                    spk_std = loader.get_signal(mode="spk", condition=std_c, area=area, session=ses)
                    if not spk_std: continue
                    
                    # Omission Window based on position (p2: 1031-1562, p3: 2062-2593, p4: 3093-3624)
                    # For simplicity, we use the relative onset
                    # DataLoader align_to='p1' gives us [0, 6000]ms
                    offsets = {"p2": 1031, "p3": 2062, "p4": 3093}
                    start = offsets[pos]
                    end = start + 500
                    
                    # Compute transient: (Mean FR Omit - Mean FR Std)
                    fr_omit = np.mean(spk_omit[0][:, o_plus_indices, start:end], axis=(0, 2)) * 1000.0
                    fr_std = np.mean(spk_std[0][:, o_plus_indices, start:end], axis=(0, 2)) * 1000.0
                    
                    transients = fr_omit - fr_std
                    results[area][pos].extend(transients.tolist())
                    
    return results
