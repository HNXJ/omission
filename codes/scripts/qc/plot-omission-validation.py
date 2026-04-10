from codes.config.paths import PROJECT_ROOT

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_omission_validation(units_path, summary_path, output_svg):
    """Plots the average Z-scored firing rate of top omission neurons."""
    # 1. Load Summary to find top units
    df = pd.read_csv(summary_path)
    mode_5 = df[df['mode_id'] == 5].copy()
    
    # Calculate Omission Index (Epoch Omission / Epoch Baseline)
    mode_5['omission_index'] = mode_5['epoch_omission'] / (mode_5['epoch_baseline'] + 1e-6)
    
    # Identify top 10 units
    top_units = mode_5.sort_values(by='omission_index', ascending=False).head(10)['unit_idx'].tolist()
    print(f"Top 10 Omission Units for validation: {top_units}")
    
    # 2. Load Unit Data
    # Shape is (190, 257, 6000) -> [units, channels, time]
    # We'll use memory mapping to save RAM
    spike_data = np.load(units_path, mmap_mode='r')
    time_axis = np.linspace(-1000, 4000, 6000)
    
    # Find indices for baseline window (-500ms to -100ms)
    baseline_indices = np.where((time_axis >= -500) & (time_axis <= -100))[0]
    
    # Store Z-scored profiles
    z_scored_profiles = []
    
    for u_idx in top_units:
        # Average across channels for this unit
        profile = np.mean(spike_data[u_idx, :, :], axis=0)
        
        # Calculate Z-score based on its own baseline
        baseline_mean = np.mean(profile[baseline_indices])
        baseline_std = np.std(profile[baseline_indices])
        
        # Avoid division by zero
        z_profile = (profile - baseline_mean) / np.maximum(baseline_std, 1e-6)
        z_scored_profiles.append(z_profile)
        
    # 3. Aggregate
    avg_z_profile = np.mean(z_scored_profiles, axis=0)
    sem_z_profile = np.std(z_scored_profiles, axis=0) / np.sqrt(len(top_units))
    
    # 4. Plot
    plt.figure(figsize=(12, 6), dpi=150)
    
    # Plot Mean and SEM
    plt.plot(time_axis, avg_z_profile, color='gold', linewidth=2, label='Average Z-Score (n=10)')
    plt.fill_between(time_axis, avg_z_profile - sem_z_profile, avg_z_profile + sem_z_profile, 
                     color='gold', alpha=0.2)
    
    # Markers
    plt.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Omission Onset (t=0)')
    plt.axvspan(-500, -100, color='gray', alpha=0.1, label='Baseline Window')
    
    # Styling
    plt.title("Omission Neuron Firing (Session 230818, Mode 5 - AAAx)")
    plt.xlabel("Time relative to omission (ms)")
    plt.ylabel("Z-Scored Firing Rate")
    plt.grid(True, alpha=0.3, linestyle=':')
    plt.xlim([-1000, 2000]) # Zoom in on the response
    plt.legend(loc='upper right')
    
    # Finalize
    os.makedirs(os.path.dirname(output_svg), exist_ok=True)
    plt.savefig(output_svg, format='svg')
    print(f"Validation plot saved to {output_svg}")

if __name__ == "__main__":
    plot_omission_validation(
        units_path=r'D:\oxm0818_units.npy',
        summary_path=str(PROJECT_ROOT / 'outputs/ses-230818_part1_summary.csv'),
        output_svg=str(PROJECT_ROOT / 'outputs/plots/ses-230818_omission_validation.svg')
    )
