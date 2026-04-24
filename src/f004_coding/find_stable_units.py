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

if __name__ == "__main__":
    results = find_highly_responsive_units()
    print(f"Found S+: {len(results['s_plus'])}")
    print(f"Found S-: {len(results['s_minus'])}")
    print(f"Found O+: {len(results['o_plus'])}")
    print(f"Found O-: {len(results['o_minus'])}")
    print(f"Found Per Area: {len(results['per_area'])}")
