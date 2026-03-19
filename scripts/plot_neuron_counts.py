
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import argparse
import os

def plot_neuron_counts_final_final(csv_path, output_dir):
    """
    Reads the detailed unit CSV, and applies the final, corrected logic for 
    assigning units from multi-area probes to get the definitive neuron counts.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return

    unique_units_df = df.drop_duplicates(subset=['session_id', 'probe_id', 'unit_idx'])

    area_order = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    area_counts = {area: 0.0 for area in area_order} # Use float for splitting V3 counts

    CHANNELS_PER_PROBE = 128
    MIDPOINT_OFFSET = CHANNELS_PER_PROBE / 2

    for _, row in unique_units_df.iterrows():
        area_str = row['area']
        probe_id = row['probe_id']
        peak_channel = row['peak_channel']
        
        probe_start_channel = probe_id * CHANNELS_PER_PROBE
        probe_midpoint = probe_start_channel + MIDPOINT_OFFSET

        assigned_area = None
        if '/' in area_str:
            try:
                area1, area2 = area_str.split('/')
                assigned_area = area1 if peak_channel < probe_midpoint else area2
            except ValueError:
                print(f"Warning: Could not parse multi-area string: {area_str}")
                continue
        else:
            assigned_area = area_str

        if assigned_area:
            if assigned_area == 'V3':
                # Per user request, V3 is split between V3d and V3a
                area_counts['V3d'] += 0.5
                area_counts['V3a'] += 0.5
            elif assigned_area in area_counts:
                area_counts[assigned_area] += 1

    # Round the values for the final report
    final_counts = {k: round(v) for k, v in area_counts.items()}
    
    labels = area_order
    values = [final_counts[area] for area in labels]

    print("--- Definitive Neuron Counts Per Area ---")
    for area, count in zip(labels, values):
        print(f"{area}: {count}")

    os.makedirs(output_dir, exist_ok=True)
    
    fig_bar = go.Figure(data=[go.Bar(x=labels, y=values, text=values, textposition='auto')])
    fig_bar.update_layout(title_text='Total Unique Neurons per Brain Area (Definitive)', xaxis_title='Brain Area', yaxis_title='Number of Neurons')
    
    fig_polar = go.Figure(data=[go.Barpolar(r=values, theta=labels, text=values, hoverinfo='r+theta')])
    fig_polar.update_layout(title_text='Total Unique Neurons per Area (Circular, Definitive)')

    try:
        fig_bar.write_html(os.path.join(output_dir, "neuron_counts_bar_definitive.html"))
        fig_bar.write_image(os.path.join(output_dir, "neuron_counts_bar_definitive.svg"))
        fig_polar.write_html(os.path.join(output_dir, "neuron_counts_circular_definitive.html"))
        fig_polar.write_image(os.path.join(output_dir, "neuron_counts_circular_definitive.svg"))
        print(f"\nSuccessfully saved all 4 definitive plot files to {output_dir}")
    except Exception as e:
        print(f"\nAn error occurred while saving the plots: {e}")

def main():
    parser = argparse.ArgumentParser(description="Plot definitive neuron counts per area from a CSV file.")
    parser.add_argument('--csv_path', type=str, default='checkpoints/omission_units_layered.csv', help='Path to the detailed unit CSV file.')
    parser.add_argument('--output_dir', type=str, default='figures', help='Directory to save the output plots.')
    args = parser.parse_args()
    
    plot_neuron_counts_final_final(args.csv_path, args.output_dir)

if __name__ == '__main__':
    main()
