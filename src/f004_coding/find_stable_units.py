import numpy as np
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
import copy

def find_highly_responsive_units(min_fr=5.0):
    """
    Finds top 20 S+, O+, S-, O- highly stable neurons, and 4 per area.
    S+ : Stimulus responsive (p1 > fixation)
    S- : Stimulus suppressed (p1 < fixation)
    O+ : Omission responsive (p2 > fixation)
    O- : Omission suppressed (p2 < fixation)
    """
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    
    all_units_stats = []
    area_top = {area: [] for area in areas}
    
    for area in areas:
        units = loader.get_units_by_area(area)
        for unit_id in units:
            # We use AXAB to get Fixation, Stimulus (p1), and Omission (p2) in one trace
            # Align to p1 (sample 1000 = 0ms)
            # Fixation: 500-1000 (-500 to 0ms)
            # p1 (Stim 1): 1000-1500 (0 to 500ms)
            # p2 (Omission): 2031-2531 (1031 to 1531ms)
            
            spk_data = loader.load_unit_spikes(unit_id, "AXAB", epoch="p1")
            if spk_data is None or spk_data.shape[0] < 10:
                continue
                
            n_trials = spk_data.shape[0]
            
            # Extract epochs and convert to Hz
            try:
                fix_data = spk_data[:, 500:1000]
                p1_data = spk_data[:, 1000:1500]
                p2_data = spk_data[:, 2031:2531]
            except IndexError:
                continue # Array too short
            
            fr_fix = np.mean(fix_data) * 1000.0
            fr_p1 = np.mean(p1_data) * 1000.0
            fr_p2 = np.mean(p2_data) * 1000.0
            
            # Overall stable FR Check
            total_time_s = spk_data.shape[1] / 1000.0
            mean_overall_fr = np.mean(np.sum(spk_data, axis=1) / total_time_s)
            
            if mean_overall_fr < min_fr:
                continue
                
            # Ratios relative to fixation
            s_ratio = (fr_p1 - fr_fix) / (fr_p1 + fr_fix + 1e-6)
            o_ratio = (fr_p2 - fr_fix) / (fr_p2 + fr_fix + 1e-6)
            
            stats = {
                'unit_id': unit_id,
                'area': area,
                'fr': mean_overall_fr,
                'fr_fix': fr_fix,
                'fr_p1': fr_p1,
                'fr_p2': fr_p2,
                's_ratio': s_ratio,
                'o_ratio': o_ratio,
                'n_trials': n_trials
            }
            
            all_units_stats.append(stats)
            area_top[area].append(stats)

    # Sort and pick top 20s
    top_20_s_plus = sorted(all_units_stats, key=lambda x: x['s_ratio'], reverse=True)[:20]
    top_20_s_minus = sorted(all_units_stats, key=lambda x: x['s_ratio'], reverse=False)[:20]
    top_20_o_plus = sorted(all_units_stats, key=lambda x: x['o_ratio'], reverse=True)[:20]
    top_20_o_minus = sorted(all_units_stats, key=lambda x: x['o_ratio'], reverse=False)[:20]
    
    # 4 per area (sorted by overall FR)
    top_4_per_area = []
    for area in areas:
        top_4 = sorted(area_top[area], key=lambda x: x['fr'], reverse=True)[:4]
        top_4_per_area.extend(top_4)
        
    return {
        's_plus': top_20_s_plus,
        's_minus': top_20_s_minus,
        'o_plus': top_20_o_plus,
        'o_minus': top_20_o_minus,
        'per_area': top_4_per_area
    }

from scipy.stats import wilcoxon

def compute_area_coding_stats():
    """
    Path B: True canonical population-counting analysis for f004.
    Definitions:
    - Fixation Window: -500 to 0ms (samples 500-1000)
    - Stimulus (S) Window: 0 to 500ms (samples 1000-1500)
    - Omission (O) Window: 1031 to 1531ms (samples 2031-2531)
    - Stable-unit criteria: min_fr >= 1.0Hz (Stable+ population)
    - Statistical Test: Wilcoxon Signed-Rank (Matched Trials)
    - Threshold: p < 0.05
    """
    loader = DataLoader()
    areas = loader.CANONICAL_AREAS
    area_stats = {}
    
    print("[action] Computing canonical population coding counts (Wilcoxon p < 0.05)...")
    
    for area in areas:
        units = loader.get_units_by_area(area)
        n_stable = 0
        n_s_plus = 0
        n_s_minus = 0
        n_o_plus = 0
        n_o_minus = 0
        
        for unit_id in units:
            # Load AXAB (contains Stim and Omission)
            spk_data = loader.load_unit_spikes(unit_id, "AXAB", epoch="p1")
            if spk_data is None or spk_data.shape[0] < 20: # Minimum trial presence
                continue
                
            total_time_s = spk_data.shape[1] / 1000.0
            mean_fr = np.mean(np.sum(spk_data, axis=1) / total_time_s)
            
            if mean_fr < 1.0: # Stable+ Criterion
                continue
            
            n_stable += 1
            
            # Extract bins (1ms resolution)
            fix_bins = np.sum(spk_data[:, 500:1000], axis=1)
            s_bins = np.sum(spk_data[:, 1000:1500], axis=1)
            o_bins = np.sum(spk_data[:, 2031:2531], axis=1)
            
            # Wilcoxon S vs Fix
            try:
                if np.any(s_bins != fix_bins):
                    _, p_s = wilcoxon(s_bins, fix_bins)
                    if p_s < 0.05:
                        if np.mean(s_bins) > np.mean(fix_bins): n_s_plus += 1
                        else: n_s_minus += 1
                
                # Wilcoxon O vs Fix
                if np.any(o_bins != fix_bins):
                    _, p_o = wilcoxon(o_bins, fix_bins)
                    if p_o < 0.05:
                        if np.mean(o_bins) > np.mean(fix_bins): n_o_plus += 1
                        else: n_o_minus += 1
            except ValueError:
                continue # Insufficient differences
                
        area_stats[area] = {
            "n_stable": n_stable,
            "n_s_plus": n_s_plus,
            "n_s_minus": n_s_minus,
            "n_o_plus": n_o_plus,
            "n_o_minus": n_o_minus,
            "test": "Wilcoxon Signed-Rank",
            "threshold": 0.05,
            "fixation_win": [-500, 0],
            "stim_win": [0, 500],
            "omission_win": [1031, 1531]
        }
        print(f"[result] {area}: S+={n_s_plus}, O+={n_o_plus} (n={n_stable})")
        
    return area_stats

if __name__ == "__main__":
    #results = find_highly_responsive_units()
    results = compute_area_coding_stats()
    # ...
