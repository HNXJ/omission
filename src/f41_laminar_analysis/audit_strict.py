import pandas as pd
import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.spiking.putative_classification import compute_waveform_metrics

loader = DataLoader()
all_units = []

# Audit loop
for area, entries in loader.area_map.items():
    for entry in entries:
        ses = entry["session"]; p = entry["probe"]
        spk_files = list((loader.data_dir.parent / "arrays").glob(f"ses{ses}-units-probe{p}-spk-*.npy"))
        
        # We need the full trial matrix for stability
        # Load all conditions and concatenate to get full trial history
        # (Assuming file structure follows session-probe-spk-CONDITION.npy)
        
        all_spk_data = []
        for f in spk_files:
            arr = np.load(f, mmap_mode='r') # (trials, units, time)
            all_spk_data.append(arr)
        
        if not all_spk_data: continue
        
        # Combine across conditions (trials, units, time)
        full_data = np.concatenate(all_spk_data, axis=0) 
        n_units = full_data.shape[1]
        
        # Calculate metrics per unit
        for i in range(n_units):
            # Unit spikes: (total_trials, time)
            u_spk = full_data[:, i, :]
            
            # 1. Firing rate (Hz)
            # Assuming 6000ms duration per trial (from earlier inspection)
            fr = np.sum(u_spk) / (u_spk.shape[0] * 6.0)
            
            # 2. Presence Ratio (using simple activity count for SNR approximation)
            # SNR: Ratio of mean activity to std of background (approx)
            trial_activity = np.sum(u_spk, axis=1)
            snr = np.mean(trial_activity) / (np.std(trial_activity) + 1e-6)
            
            # 3. Stable-Plus criteria: FR > 1, SNR > 0.8, All trials active
            is_stable = (fr > 1.0) and (snr > 0.5)
            is_stable_plus = (fr > 1.0) and (snr > 0.8) and (np.all(trial_activity > 0))
            
            all_units.append({
                "area": area,
                "total": 1,
                "stable": int(is_stable),
                "stable_plus": int(is_stable_plus)
            })

df = pd.DataFrame(all_units)
summary = df.groupby('area').sum()
print(summary)
summary.to_csv("D:/drive/outputs/oglo-8figs/f041_laminar_analysis/strict_population_summary.csv")
