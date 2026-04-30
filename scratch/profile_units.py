import numpy as np
import pandas as pd
from pathlib import Path
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def profile_units():
    """
    Searches for units matching activity profiles across stimulus repetitions.
    x = p3, y = p1
    z = d3, w = d1
    """
    print(f"""[action] Initializing DataLoader...""")
    loader = DataLoader()
    
    # Timing constants (ms relative to p1 onset)
    # Period duration = 515ms, Cycle = 1031ms
    P_DUR = 515
    CYCLE = 1031
    
    # Offsets in array (assuming 1000ms baseline before p1)
    BASE_OFFSET = 1000
    
    p1_slice = slice(BASE_OFFSET, BASE_OFFSET + P_DUR)
    d1_slice = slice(BASE_OFFSET + P_DUR, BASE_OFFSET + CYCLE)
    p3_slice = slice(BASE_OFFSET + 2*CYCLE, BASE_OFFSET + 2*CYCLE + P_DUR)
    d3_slice = slice(BASE_OFFSET + 2*CYCLE + P_DUR, BASE_OFFSET + 3*CYCLE)
    
    print(f"""[action] Window slices defined: p1={p1_slice}, d1={d1_slice}, p3={p3_slice}, d3={d3_slice}""")
    
    conditions = ["AXAB", "BXBA", "RXRR"]
    areas = loader.CANONICAL_AREAS
    
    summary_results = []
    
    for area in areas:
        print(f"""[action] Processing area: {area}""")
        units = loader.get_units_by_area(area)
        if not units: continue
        
        for unit_id in units:
            print(f"""[action] Profiling unit: {unit_id}""")
            
            unit_profiles = {}
            valid_unit = True
            
            for cond in conditions:
                print(f"""[action] Loading {cond} for {unit_id}""")
                spk = loader.load_unit_spikes(unit_id, condition=cond)
                if spk is None or spk.size == 0:
                    valid_unit = False
                    break
                
                # Compute mean firing rates across trials and time
                y_val = np.mean(spk[:, p1_slice]) * 1000 # Hz
                w_val = np.mean(spk[:, d1_slice]) * 1000 # Hz
                x_val = np.mean(spk[:, p3_slice]) * 1000 # Hz
                z_val = np.mean(spk[:, d3_slice]) * 1000 # Hz
                
                unit_profiles[cond] = {'x': x_val, 'y': y_val, 'z': z_val, 'w': w_val}
            
            if not valid_unit: continue
            
            # Aggregate across conditions (mean activity)
            x_avg = np.mean([p['x'] for p in unit_profiles.values()])
            y_avg = np.mean([p['y'] for p in unit_profiles.values()])
            z_avg = np.mean([p['z'] for p in unit_profiles.values()])
            w_avg = np.mean([p['w'] for p in unit_profiles.values()])
            
            # Baseline activity filter (ignore dead units)
            if y_avg < 1.0 and x_avg < 1.0: continue
            
            # Ratios
            ratio_xy = x_avg / y_avg if y_avg > 0 else 0
            ratio_zw = z_avg / w_avg if w_avg > 0 else 0
            
            entry = {
                'unit_id': unit_id,
                'area': area,
                'x': x_avg, 'y': y_avg, 'z': z_avg, 'w': w_avg,
                'ratio_xy': ratio_xy,
                'ratio_zw': ratio_zw
            }
            summary_results.append(entry)
            print(f"""[action] Unit {unit_id} summary: x={x_avg:.2f}, y={y_avg:.2f}, ratio={ratio_xy:.2f}""")

    df = pd.DataFrame(summary_results)
    print(f"""[action] Total units profiled: {len(df)}""")
    
    # Apply Filters as requested
    filters = {
        "x > y": df[df['x'] > df['y']],
        "x > 1.5y": df[df['x'] > 1.5 * df['y']],
        "x > 2.0y": df[df['x'] > 2.0 * df['y']],
        "x < y": df[df['x'] < df['y']],
        "x < 0.66y": df[df['x'] < (1.0/1.5) * df['y']], # Interpreting x < 1.5y logic as y > 1.5x
        "x < 0.5y": df[df['x'] < 0.5 * df['y']]
    }
    
    for name, filtered_df in filters.items():
        print(f"""[action] Filter {name}: Found {len(filtered_df)} units.""")
        # Save results to CSV for each filter
        out_path = Path("scratch") / f"units_profile_{name.replace(' ', '').replace('>', 'gt').replace('<', 'lt')}.csv"
        filtered_df.to_csv(out_path, index=False)
        print(f"""[action] Saved to {out_path}""")

    return df

if __name__ == "__main__":
    profile_units()
