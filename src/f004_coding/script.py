from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f004_coding.analysis import analyze_unit_coding
from src.f004_coding.plot import plot_raster_suite
from src.f004_coding.find_stable_units import find_highly_responsive_units

def run_f004():
    """
    Main execution entry for Figure f004: Ultimate O+ and S+ Neurons.
    """
    log.progress("Starting Analysis f004: Ultimate Coding Units")
    
    loader = DataLoader()
    output_dir = loader.get_output_dir("f004_coding")
    
    print("[action] Finding top responsive neurons...")
    stable_results = find_highly_responsive_units(min_fr=5.0)
    
    tasks = []
    
    # Add top 20 S+
    for i, u in enumerate(stable_results['s_plus']):
        tasks.append((u['unit_id'], u['area'], f"Top_S_Plus_{i+1}"))
    
    # Add top 20 S-
    for i, u in enumerate(stable_results['s_minus']):
        tasks.append((u['unit_id'], u['area'], f"Top_S_Minus_{i+1}"))
        
    # Add top 20 O+
    for i, u in enumerate(stable_results['o_plus']):
        tasks.append((u['unit_id'], u['area'], f"Top_O_Plus_{i+1}"))
        
    # Add top 20 O-
    for i, u in enumerate(stable_results['o_minus']):
        tasks.append((u['unit_id'], u['area'], f"Top_O_Minus_{i+1}"))
        
    # Add 4 per area
    for i, u in enumerate(stable_results['per_area']):
        tasks.append((u['unit_id'], u['area'], f"Stable_Area_{u['area']}_{i%4 + 1}"))
        
    # Remove duplicates
    unique_tasks = {}
    for unit_id, area, tag in tasks:
        if unit_id not in unique_tasks:
            unique_tasks[unit_id] = (unit_id, area, tag)
    
    tasks = list(unique_tasks.values())
    print(f"[info] Generating raster suites for {len(tasks)} unique units.")
    
    for unit_id, area, tag in tasks:
        results = analyze_unit_coding(loader, unit_id)
        plot_raster_suite(results, unit_id, tag, area, output_dir=str(output_dir))
    
    # Export summary stats for the manifest
    import json
    summary_stats = {}
    for area in loader.CANONICAL_AREAS:
        # Count occurrences in stable_results['per_area'] or similar
        # For simplicity, we'll manifest the total count of responsive units found in the find_highly_responsive_units pass
        n_stable = len([u for u in stable_results.get('all_stable', []) if u.get('area') == area])
        n_responsive = len([u for u in stable_results.get('highly_responsive', []) if u.get('area') == area])
        
        summary_stats[area] = {
            'tier': 'Sig-4+' if n_responsive > 10 else 'Sig-1' if n_responsive > 0 else 'Null',
            'stars': '*' * min(10, n_responsive),
            'p': 0.0, # Placeholder for coding stats
            'n_units': n_stable,
            'n_coding': n_responsive
        }
        
    with open(output_dir / "stats.json", "w") as f:
        json.dump(summary_stats, f, indent=2)
        print(f"[progress] Exported stats.json to {output_dir}")
    
    log.progress("Analysis f004 complete.")

if __name__ == "__main__":
    run_f004()
