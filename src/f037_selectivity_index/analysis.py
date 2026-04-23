# beta
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def analyze_selectivity_index(loader: DataLoader, areas: list, condition="AXAB"):
    """
    Computes Stimulus Selectivity Index (SSI).
    SSI = (R_pref - R_nonpref) / (R_pref + R_nonpref)
    """
    results = {}
    
    # Define timing windows relative to omission onset (p2=1031)
    # Ghost window: 0 to 500ms post-omission
    ghost_start = 1031
    ghost_end = 1031 + 500
    
    for area in areas:
        log.info(f"Computing Selectivity Index for {area}")
        print(f"""[f037] Processing area: {area}""")
        
        # In this context, 'Pref' is the expected stimulus in the AXAB sequence (B)
        # 'NonPref' is a control stimulus or baseline.
        # Here we compare predictable response (p1) vs omission response (p2)
        # to see if neurons remain 'tuned' to the missing stimulus.
        
        # Load stable-plus units for area
        units = loader.get_units_by_area(area)
        if not units: continue
        
        area_ssi = []
        for unit_id in units:
            # Load trial data for predictable (p1) and omission (p2)
            # Shapes: (n_trials, n_timepoints)
            p1_data = loader.load_unit_spikes(unit_id, epoch="p1") # Predictable B
            p2_data = loader.load_unit_spikes(unit_id, epoch="p2") # Omission B
            
            if p1_data is None or p2_data is None: continue
            
            # Mean rates in the response window
            r_pref = np.mean(p1_data[:, ghost_start:ghost_end])
            r_omission = np.mean(p2_data[:, ghost_start:ghost_end])
            
            # SSI calculation
            denom = r_pref + r_omission
            if denom > 1e-5:
                ssi = (r_pref - r_omission) / denom
                area_ssi.append(ssi)
        
        if area_ssi:
            results[area] = {
                "ssi_mean": np.mean(area_ssi),
                "ssi_sem": np.std(area_ssi) / np.sqrt(len(area_ssi)),
                "n_units": len(area_ssi)
            }
            print(f"""[f037] {area}: SSI Mean = {results[area]['ssi_mean']:.3f} (n={len(area_ssi)})""")
            
    return results
