import pandas as pd
import numpy as np
from src.analysis.io.loader import DataLoader

loader = DataLoader()
lifecycle_data = []

# Lifecycle analysis loop
for area, entries in loader.area_map.items():
    for entry in entries:
        ses = entry["session"]; p = entry["probe"]
        spk_files = list((loader.data_dir.parent / "arrays").glob(f"ses{ses}-units-probe{p}-spk-*.npy"))
        if not spk_files: continue
        
        all_spk_data = [np.load(f, mmap_mode='r') for f in spk_files]
        full_data = np.concatenate(all_spk_data, axis=0) # (trials, units, time)
        n_trials, n_units, _ = full_data.shape
        
        for i in range(n_units):
            # Trial activity (n_trials,)
            activity = np.sum(full_data[:, i, :], axis=1)
            active_trials = np.where(activity > 0)[0]
            
            if len(active_trials) == 0:
                continue # Never active
            
            first = active_trials[0]
            last = active_trials[-1]
            
            # Categories:
            # 1. Permanent (first == 0 and last == n_trials-1)
            # 2. Sudden Disappearance (last < n_trials - 1)
            # 3. Delayed Emergence (first > 0)
            
            cat = "Stable"
            if first > 0 and last == n_trials - 1:
                cat = "Delayed Emergence"
            elif first == 0 and last < n_trials - 1:
                cat = "Sudden Disappearance"
            elif first > 0 and last < n_trials - 1:
                cat = "Transient"
                
            lifecycle_data.append({"area": area, "category": cat})

df = pd.DataFrame(lifecycle_data)
summary = df.groupby(['area', 'category']).size().unstack(fill_value=0)
print(summary)
summary.to_csv("D:/drive/outputs/oglo-8figs/f041_laminar_analysis/lifecycle_summary.csv")
