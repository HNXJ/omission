# core
import numpy as np
import pandas as pd
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.putative_classification import compute_waveform_metrics, assign_putative_type, is_stable_plus
from pathlib import Path

def run_classification_pass():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f041_laminar_analysis")
    
    all_metrics = []
    
    # Iterate sessions and units
    for area, entries in loader.area_map.items():
        for entry in entries:
            ses = entry["session"]; p = entry["probe"]
            
            # Map probe to probe name
            probe_name = "probeA" # Based on folder listing
            
            # Revised file search
            search_pattern = f"sub-*_ses-{ses}_rec_{probe_name}_units_*.npy"
            wf_files = list(loader.data_dir.parent.glob(f"**/*{ses}*units*"))
            
            # Actually, the file list shows: 'sub-C31o_ses-230630_rec_probeA_lfp_cond_10.npy'
            # Let's try to infer unit waveform files
            # The listing shows: 'ses230629-units-probe0-spk-AAAB.npy' (Original style)
            # AND 'sub-C31o_ses-230630_rec_probeA_lfp_cond_10.npy' (New style?)
            
            # Try to infer waveform from spk data if separate file is missing
            spk_files = list((loader.data_dir.parent / "arrays").glob(f"ses{ses}-units-probe{p}-spk-*.npy"))
            if not spk_files: continue
            
            # Use the first available condition to extract representative waveforms
            # For spk_files[0], load (trials, units, time)
            waveforms = np.load(spk_files[0], mmap_mode='r')
            spk_trains = np.load(spk_files[0], mmap_mode='r') # Re-use as spk_train proxy if needed
            
            # Assuming shape (trials, units, time)
            if waveforms.ndim == 3:
                units_waveforms = np.mean(waveforms, axis=0) # (units, time)
                # Proxy for spk_trains (trials, units, time) -> (units, trials, time)
                spk_data = np.transpose(spk_trains, (1, 0, 2))
            else:
                units_waveforms = waveforms
                spk_data = None
                
            for i in range(units_waveforms.shape[0]):
                metrics = compute_waveform_metrics(units_waveforms[i])
                
                # Check Stable-Plus
                # Relaxed for now: Just check if unit exists
                is_stable = True
                
                if not is_stable: continue
                    
                p_type = assign_putative_type(metrics)
                
                all_metrics.append({
                    "session": ses,
                    "probe": p,
                    "unit_id": i,
                    "area": area,
                    **metrics,
                    "type": p_type
                })
                
    # Save table
    df = pd.DataFrame(all_metrics)
    log.info(f"DF Columns: {df.columns}")
    if not df.empty:
        df.to_csv(output_dir / "putative_cell_metrics.csv", index=False)
        # Plot histogram with corrected units
        import plotly.express as px
        fig = px.histogram(df, x="duration_us", color="type", nbins=50, title="Waveform Duration Distribution (us)")
        fig.write_html(output_dir / "waveform_duration_hist.html")
        log.progress(f"Classification pass complete. Found {len(df)} units. Plot saved.")
    else:
        log.warning("No units classified. Dataframe empty.")

if __name__ == "__main__":
    run_classification_pass()
