# f039 — Spike-Field Coherence Pipeline Script
# =============================================
# Orchestrates the full PPC pipeline:
# 1. Load spike and LFP data per area pair / condition
# 2. Compute PPC per unit-LFP pair per band
# 3. Aggregate across units with +/- SEM
# 4. Generate interactive Plotly HTML figures

import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f039_spike_field_coherence.analysis import (
    BANDS, TIMING_MAP, MIN_SPIKES,
    compute_ppc, bandpass_filter, extract_spike_phases,
    match_spike_counts, compute_sfc_for_pair,
)
from src.f039_spike_field_coherence.plot import (
    plot_ppc_band_comparison, plot_ppc_per_area,
)


def run_f039():
    """
    Main entry point for f039: Spike-Field Coherence via PPC.
    
    Evaluates phase synchronization between localized unit spiking
    and distal LFP across 5 frequency bands and all omission conditions.
    """
    print(f"""[action] === Starting f039: Spike-Field Coherence (PPC) ===""")
    log.action("Starting f039: Spike-Field Coherence (PPC)")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f039_spike_field_coherence")
    print(f"""[info] Output directory: {output_dir}""")
    
    # Analysis pairs: V1 spikes -> PFC LFP (canonical FF+FB routing)
    # Also: PFC spikes -> V1 LFP (reverse direction)
    analysis_pairs = [
        ("V1", "PFC"),   # V1 unit spiking vs PFC LFP
        ("PFC", "V1"),   # PFC unit spiking vs V1 LFP
    ]
    
    # Conditions with their omission positions
    conditions = list(TIMING_MAP.keys())
    print(f"""[info] Analyzing {len(analysis_pairs)} pairs x {len(conditions)} conditions x {len(BANDS)} bands""")
    
    all_results = []
    
    for area_spk, area_lfp in analysis_pairs:
        print(f"""\n{'='*60}""")
        print(f"""[action] Processing: {area_spk} spikes vs {area_lfp} LFP""")
        print(f"""{'='*60}""")
        
        for cond in conditions:
            print(f"""\n[action] Condition: {cond} (slot: {TIMING_MAP[cond]})""")
            
            # Load data aligned to omission
            spk_list = loader.get_signal(mode="spk", area=area_spk, condition=cond, align_to="omission")
            lfp_list = loader.get_signal(mode="lfp", area=area_lfp, condition=cond, align_to="omission")
            
            if not spk_list or not lfp_list:
                print(f"""[warning] Missing data for {area_spk}/{area_lfp}/{cond}, skipping""")
                continue
            
            print(f"""[info] Loaded {len(spk_list)} spike sessions, {len(lfp_list)} LFP sessions""")
            
            # Omission onset in the aligned window
            # Data is aligned to [-1000, +1000]ms around omission
            # So omission onset is at sample 1000 (center of the window)
            omission_onset_sample = 1000
            
            for band_name, (low_hz, high_hz) in BANDS.items():
                print(f"""\n[action] Band: {band_name} ({low_hz}-{high_hz}Hz)""")
                
                ppc_baseline_list = []
                ppc_omission_list = []
                n_valid_pairs = 0
                
                # Process each session pair
                n_sessions = min(len(spk_list), len(lfp_list))
                
                for sess_idx in range(n_sessions):
                    spk_sess = spk_list[sess_idx]  # (trials, units, time)
                    lfp_sess = lfp_list[sess_idx]   # (trials, channels, time)
                    
                    n_trials = min(spk_sess.shape[0], lfp_sess.shape[0])
                    n_units = spk_sess.shape[1]
                    n_channels = lfp_sess.shape[1]
                    
                    print(f"""[info] Session {sess_idx}: {n_trials} trials, {n_units} units, {n_channels} LFP channels""")
                    
                    if n_trials < 3:
                        print(f"""[warning] Too few trials ({n_trials}), skipping session""")
                        continue
                    
                    # Sample units and channels to keep computation tractable
                    # Use up to 20 units and the mean LFP across channels
                    max_units = min(20, n_units)
                    unit_indices = np.random.choice(n_units, max_units, replace=False) if n_units > max_units else range(n_units)
                    
                    # Mean LFP across channels (population LFP)
                    lfp_mean = np.mean(lfp_sess[:n_trials, :, :], axis=1)  # (trials, time)
                    print(f"""[info] Using {len(unit_indices)} units, mean LFP across {n_channels} channels""")
                    
                    for u_idx in unit_indices:
                        # Extract spike train for this unit
                        spk_unit = spk_sess[:n_trials, u_idx, :]  # (trials, time)
                        
                        # Check minimum spike count across all trials
                        total_spikes_base = 0
                        total_spikes_omit = 0
                        baseline_start = max(0, omission_onset_sample - 500)
                        baseline_end = omission_onset_sample
                        omission_start = omission_onset_sample
                        omission_end = min(omission_onset_sample + 500, spk_unit.shape[-1])
                        
                        for t in range(n_trials):
                            total_spikes_base += np.sum(spk_unit[t, baseline_start:baseline_end])
                            total_spikes_omit += np.sum(spk_unit[t, omission_start:omission_end])
                        
                        # Enforce minimum spike threshold
                        if total_spikes_base < MIN_SPIKES or total_spikes_omit < MIN_SPIKES:
                            continue
                        
                        # Compute PPC for this unit-LFP pair
                        try:
                            result = compute_sfc_for_pair(
                                spk_data=spk_unit,
                                lfp_data=lfp_mean,
                                omission_onset_sample=omission_onset_sample,
                                band=(low_hz, high_hz),
                                window_ms=500,
                                fs=1000
                            )
                            
                            if not np.isnan(result['ppc_baseline']) and not np.isnan(result['ppc_omission']):
                                ppc_baseline_list.append(result['ppc_baseline'])
                                ppc_omission_list.append(result['ppc_omission'])
                                n_valid_pairs += 1
                        except Exception as e:
                            print(f"""[warning] PPC computation failed for unit {u_idx}: {e}""")
                            continue
                
                # Aggregate across all valid unit-LFP pairs
                if n_valid_pairs > 0:
                    ppc_base_arr = np.array(ppc_baseline_list)
                    ppc_omit_arr = np.array(ppc_omission_list)
                    
                    result_row = {
                        "area_src": area_spk,
                        "area_tgt": area_lfp,
                        "condition": cond,
                        "band": band_name,
                        "ppc_baseline_mean": np.mean(ppc_base_arr),
                        "ppc_baseline_sem": np.std(ppc_base_arr) / np.sqrt(n_valid_pairs),
                        "ppc_omission_mean": np.mean(ppc_omit_arr),
                        "ppc_omission_sem": np.std(ppc_omit_arr) / np.sqrt(n_valid_pairs),
                        "ppc_delta": np.mean(ppc_omit_arr) - np.mean(ppc_base_arr),
                        "n_pairs": n_valid_pairs,
                    }
                    
                    print(f"""[result] {cond}/{band_name}: PPC_base={result_row['ppc_baseline_mean']:.4f} +/- {result_row['ppc_baseline_sem']:.4f}""")
                    print(f"""         PPC_omit={result_row['ppc_omission_mean']:.4f} +/- {result_row['ppc_omission_sem']:.4f}""")
                    print(f"""         Delta={result_row['ppc_delta']:.4f}, n_pairs={n_valid_pairs}""")
                    
                    all_results.append(result_row)
                else:
                    print(f"""[warning] No valid pairs for {cond}/{band_name}""")
    
    # Save results
    if all_results:
        results_df = pd.DataFrame(all_results)
        csv_path = output_dir / "f039_ppc_results.csv"
        results_df.to_csv(csv_path, index=False)
        print(f"""\n[action] Saved {len(results_df)} result rows to {csv_path}""")
        
        # Generate figures
        print(f"""\n[action] Generating figures...""")
        plot_ppc_band_comparison(results_df, str(output_dir))
        plot_ppc_per_area(results_df, str(output_dir))
        
        # Summary statistics
        print(f"""\n{'='*60}""")
        print(f"""[SUMMARY] f039 Spike-Field Coherence Results""")
        print(f"""{'='*60}""")
        print(f"""Total result rows: {len(results_df)}""")
        print(f"""Area pairs: {results_df[['area_src','area_tgt']].drop_duplicates().values.tolist()}""")
        print(f"""Conditions analyzed: {results_df['condition'].unique().tolist()}""")
        print(f"""Bands: {results_df['band'].unique().tolist()}""")
        
        # Find strongest PPC changes
        if 'ppc_delta' in results_df.columns:
            top_delta = results_df.nlargest(5, 'ppc_delta')
            print(f"""\nTop 5 PPC increases (omission > baseline):""")
            for _, row in top_delta.iterrows():
                print(f"""  {row['area_src']}->{row['area_tgt']} {row['condition']}/{row['band']}: delta={row['ppc_delta']:.4f} (n={row['n_pairs']})""")
            
            bot_delta = results_df.nsmallest(5, 'ppc_delta')
            print(f"""\nTop 5 PPC decreases (baseline > omission):""")
            for _, row in bot_delta.iterrows():
                print(f"""  {row['area_src']}->{row['area_tgt']} {row['condition']}/{row['band']}: delta={row['ppc_delta']:.4f} (n={row['n_pairs']})""")
    else:
        print(f"""[error] No valid results produced""")
    
    print(f"""\n[action] === f039 Complete ===""")
    log.progress("f039: Spike-Field Coherence pipeline complete")


if __name__ == "__main__":
    run_f039()
