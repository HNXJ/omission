import pandas as pd
import numpy as np
from src.analysis.io.loader import DataLoader

def has_silence_streak(trial_activity, min_streak=100):
    """Checks for a streak of min_streak or more trials with zero activity."""
    # trial_activity: (n_trials,) boolean or integer array
    is_zero = (trial_activity == 0)
    # Find streaks
    diff = np.diff(np.concatenate(([0], is_zero.astype(int), [0])))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]
    lengths = ends - starts
    return np.any(lengths >= min_streak)

loader = DataLoader()
dropout_data = []

# Audit loop
for area, entries in loader.area_map.items():
    for entry in entries:
        ses = entry["session"]; p = entry["probe"]
        spk_files = list((loader.data_dir.parent / "arrays").glob(f"ses{ses}-units-probe{p}-spk-*.npy"))
        
        if not spk_files: continue
        
        all_spk_data = [np.load(f, mmap_mode='r') for f in spk_files]
        full_data = np.concatenate(all_spk_data, axis=0) 
        n_units = full_data.shape[1]
        
        for i in range(n_units):
            # Unit trial activity: (n_trials,)
            trial_activity = np.sum(full_data[:, i, :], axis=1)
            streak = has_silence_streak(trial_activity)
            
            dropout_data.append({
                "area": area,
                "has_streak": int(streak)
            })

df = pd.DataFrame(dropout_data)
summary = df.groupby('area')['has_streak'].sum().reset_index()
print(summary)
summary.to_csv("D:/drive/outputs/oglo-8figs/f041_laminar_analysis/dropout_summary.csv")
