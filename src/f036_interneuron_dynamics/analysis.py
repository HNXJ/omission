# beta
import numpy as np
import pandas as pd
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.spiking.putative_classification import compute_waveform_metrics, assign_putative_type

def analyze_interneuron_dynamics(loader: DataLoader):
    """
    Analyzes dynamics of putative interneurons (FS) vs pyramidal cells (RS).
    Utilizes pre-extracted CSV metrics for speed and 'Stable-Plus' filtering.
    """
    sessions = loader.get_sessions()
    areas = ['V1', 'V4', 'PFC']
    
    results = {
        'FS': {area: [] for area in areas},
        'RS': {area: [] for area in areas},
        'metadata': {'counts': {area: {'FS': 0, 'RS': 0} for area in areas}}
    }
    
    for ses in sessions:
        log.info(f"Analyzing Interneuron Dynamics (Stable-Plus) for Session: {ses}")
        metrics_df = loader.get_unit_metrics(ses)
        if metrics_df is None: 
            log.warning(f"No unit metrics found for {ses}")
            continue
            
        for area in areas:
            # Load spike data
            spk_list = loader.get_signal(mode="spk", condition="RRRR", area=area, session=ses)
            if not spk_list: continue
            
            # Match with area mapping to find unit indices
            area_entries = [e for e in loader.area_map.get(area, []) if e['session'] == ses]
            
            unit_offset = 0
            for entry in area_entries:
                probe = entry['probe']
                # Filter metrics for this probe
                # In NWB, peak_channel_id usually corresponds to the probe's channel index
                # But here we rely on the order in the units table
                
                # Load the full file just to get unit count for this probe
                filename = f"ses{ses}-units-probe{probe}-spk-RRRR.npy"
                file_path = loader.data_dir / filename
                if not file_path.exists(): continue
                
                arr = np.load(file_path, mmap_mode='r')
                n_probe_units = arr.shape[1]
                
                # 1. Map global peak_channel_id to identify units for this probe
                # Canonical: 128 channels per probe (Sequential)
                ch_total = entry.get('total_ch', 128)
                p_start = probe * ch_total
                p_end = (probe + 1) * ch_total
                
                # metrics_df is the full session unit table
                probe_metrics = metrics_df[(metrics_df['peak_channel_id'] >= p_start) & 
                                          (metrics_df['peak_channel_id'] < p_end)]
                
                if len(probe_metrics) != n_probe_units:
                    log.warning(f"Unit count mismatch for ses {ses} probe {probe}: CSV={len(probe_metrics)}, NPY={n_probe_units}")
                
                # Area boundaries (global)
                a_start = p_start + entry['start_ch']
                a_end = p_start + entry['end_ch']
                
                for i, (idx, row) in enumerate(probe_metrics.iterrows()):
                    # Check area membership by peak channel
                    ch = row.get('peak_channel_id')
                    if ch < a_start or ch >= a_end:
                        continue

                    # Stable-Plus Filter (Mandate: FR>1Hz, SNR>0.8, 100% presence)
                    # We use 0.98 as 100% proxy due to metadata rounding
                    snr = row.get('snr', 0)
                    pr = row.get('presence_ratio', 0)
                    fr = row.get('firing_rate', 0)
                    
                    if snr < 0.8 or pr < 0.98 or fr < 1.0:
                        continue
                        
                    duration = row.get('waveform_duration', 1.0) # Values in ms (e.g. 0.3)
                    u_type = "FS" if duration < 0.4 else "RS" # 400us threshold (0.4ms)
                    
                    # PSTH (index i corresponds to the i-th unit in the probe's .npy file)
                    psth = np.mean(arr[:, i, :], axis=0) * 1000.0
                    
                    results[u_type][area].append(psth)
                    results['metadata']['counts'][area][u_type] += 1

    # Final averaging
    for u_type in ['FS', 'RS']:
        for area in areas:
            if results[u_type][area]:
                psths = np.array(results[u_type][area])
                results[u_type][area] = {
                    'avg': np.mean(psths, axis=0),
                    'sem': np.std(psths, axis=0) / np.sqrt(len(psths))
                }
            else:
                results[u_type][area] = None
                
    return results

    return results
