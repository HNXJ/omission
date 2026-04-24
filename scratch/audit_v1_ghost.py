
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.spiking.stats import detect_ramping_units

def audit_v1_ghost():
    loader = DataLoader()
    area = "V1"
    cond = "AXAB"
    
    # Check sessions with AXAB data
    sessions = loader.get_sessions()
    
    for ses in sessions:
        if ses in loader.BLACKLISTED_SESSIONS:
            continue
            
        spk_list = loader.get_signal(mode="spk", condition=cond, area=area, session=ses)
        if not spk_list:
            continue
            
        for i, spk_arr in enumerate(spk_list):
            # Try different windows
            windows = [
                (1531, 2031), # Pre-P2 (Omission)
                (531, 1031),  # Pre-P1
                (1031, 1531)  # During P1
            ]
            
            print(f"\n--- Session {ses}, Area {area}, Index {i} (Units: {spk_arr.shape[1]}) ---")
            for win in windows:
                slopes, r2 = detect_ramping_units(spk_arr, window=win)
                # Lower threshold for V1 as per plan
                valid = (slopes > 0.001) & (r2 > 0.05)
                n_valid = np.sum(valid)
                max_r2 = np.max(r2) if len(r2) > 0 else 0
                print(f"  Window {win}: Found {n_valid} rampers. Max R2: {max_r2:.4f}")

if __name__ == "__main__":
    audit_v1_ghost()
