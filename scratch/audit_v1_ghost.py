
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.spiking.stats import detect_ramping_units

def audit_v1_ghost():
    loader = DataLoader()
    area = "V1"
    cond = "AXAB"
    
    # Check all sessions
    sessions = ["230630", "230701", "230702", "230703", "230704", "230901"]
    
    for ses in sessions:
        if ses in loader.BLACKLISTED_SESSIONS:
            print(f"Session {ses} is blacklisted.")
            continue
            
        spk_list = loader.get_signal(mode="spk", condition=cond, area=area, session=ses)
        if not spk_list:
            print(f"No AXAB data for {area} in session {ses}")
            continue
            
        for i, spk_arr in enumerate(spk_list):
            print(f"Session {ses}, Probe {i}: Shape {spk_arr.shape}")
            
            # Try different windows
            windows = [
                (1531, 2031), # Current (wrong?)
                (531, 1031),  # Before 2nd stim (correct for AXAB omission?)
                (1031, 1531)  # During 2nd stim (omission window)
            ]
            
            for win in windows:
                slopes, r2 = detect_ramping_units(spk_arr, window=win)
                valid = (slopes > 0.001) & (r2 > 0.1)
                n_valid = np.sum(valid)
                print(f"  Window {win}: Found {n_valid} rampers. Max Slope: {np.max(slopes) if len(slopes)>0 else 0:.4f}")

if __name__ == "__main__":
    audit_v1_ghost()
