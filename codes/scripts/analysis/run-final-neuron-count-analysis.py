
import sys
import os
import glob
import argparse
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
from pynwb import NWBHDF5IO
import numpy as np
from codes.config.paths import DATA_DIR, FIGURES_DIR

# Mapping dictionary for specific aliases
AREA_MAPPING = {
    'DP': 'V4',
    'V3': ['V3d', 'V3a'] # V3 will be split further
}

def get_definitive_neuron_counts_v2():
    """
    Iterates through all NWB files and correctly assigns units to areas
    handling combined labels and the DP->V4 mapping.
    """
    nwb_files = glob.glob(str(DATA_DIR / 'sub-*_ses-*_rec.nwb'))
    if not nwb_files:
        print("Error: No NWB files found in the 'data/' directory.")
        return None

    target_areas = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    total_area_counts = defaultdict(float) # Use float for potential splitting

    print(f"Found {len(nwb_files)} NWB files to process...")

    for nwb_path in nwb_files:
        print(f"  - Processing {os.path.basename(nwb_path)}...")
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                
                if nwbfile.units is None or nwbfile.electrodes is None:
                    continue

                units_df = nwbfile.units.to_dataframe()
                electrodes_df = nwbfile.electrodes.to_dataframe()

                # Get peak channel and group info for each unit
                for _, unit in units_df.iterrows():
                    peak_chan_id = int(float(unit['peak_channel_id']))
                    
                    # Find electrode and its location/label
                    if peak_chan_id not in electrodes_df.index:
                        continue
                    
                    elec = electrodes_df.loc[peak_chan_id]
                    raw_label = elec.get('location', elec.get('label', 'unknown'))
                    if isinstance(raw_label, bytes):
                        raw_label = raw_label.decode('utf-8')
                    
                    # 1. Clean and split the label
                    # Replace '/' with ',' to treat them the same
                    clean_label = raw_label.replace('/', ',')
                    areas_in_probe = [a.strip() for a in clean_label.split(',')]
                    
                    # 2. Map DP to V4
                    areas_in_probe = [AREA_MAPPING.get(a, a) for a in areas_in_probe]
                    
                    # Flatten list if V3 was mapped to [V3d, V3a]
                    final_areas = []
                    for a in areas_in_probe:
                        if isinstance(a, list):
                            final_areas.extend(a)
                        else:
                            final_areas.append(a)
                    
                    num_areas = len(final_areas)
                    
                    # 3. Assign to area based on channel position
                    # Probe ID is inferred from the peak channel (0-127, 128-255, etc)
                    CHANNELS_PER_PROBE = 128
                    channel_in_probe = peak_chan_id % CHANNELS_PER_PROBE
                    
                    # Divide probe channels by number of areas
                    segment_width = CHANNELS_PER_PROBE / num_areas
                    area_index = int(channel_in_probe // segment_width)
                    area_index = min(area_index, num_areas - 1) # Cap index
                    
                    assigned_area = final_areas[area_index]
                    
                    if assigned_area in target_areas:
                        total_area_counts[assigned_area] += 1
                        
        except Exception as e:
            print(f"    -> ERROR processing file {nwb_path}: {e}")
            continue
            
    return total_area_counts

def plot_counts(area_counts, area_order, output_dir):
    if not area_counts:
        print("No area counts to plot.")
        return

    labels = area_order
    values = [int(round(area_counts.get(area, 0))) for area in labels]

    print("--- Definitive Neuron Counts Per Area (Corrected Logic) ---")
    for area, count in zip(labels, values):
        print(f"{area}: {count}")

    os.makedirs(output_dir, exist_ok=True)
    
    fig_bar = go.Figure(data=[go.Bar(x=labels, y=values, text=values, textposition='auto')])
    fig_bar.update_layout(title_text='Total Unique Neurons per Brain Area (Definitive Corrected)', xaxis_title='Brain Area', yaxis_title='Number of Neurons')
    
    fig_polar = go.Figure(data=[go.Barpolar(r=values, theta=labels, text=values, hoverinfo='r+theta')])
    fig_polar.update_layout(title_text='Total Unique Neurons per Area (Circular, Definitive Corrected)')

    try:
        fig_bar.write_html(output_dir / "neuron_counts_bar_definitive_v2.html")
        fig_bar.write_image(output_dir / "neuron_counts_bar_definitive_v2.svg")
        fig_polar.write_html(output_dir / "neuron_counts_circular_definitive_v2.html")
        fig_polar.write_image(output_dir / "neuron_counts_circular_definitive_v2.svg")
        print(f"Successfully saved all 4 definitive plot files to {output_dir}")
    except Exception as e:
        print(f"An error occurred while saving the plots: {e}")

def main():
    parser = argparse.ArgumentParser(description="Get and plot definitive neuron counts with area mapping.")
    parser.add_argument('--output_dir', type=str, default=str(FIGURES_DIR), help='Directory to save the output plots.')
    args = parser.parse_args()

    final_counts = get_definitive_neuron_counts_v2()
    plot_counts(final_counts, ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC'], args.output_dir)

if __name__ == '__main__':
    main()
