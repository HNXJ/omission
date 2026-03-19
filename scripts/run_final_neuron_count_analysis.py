
import sys
import os
import glob
import argparse
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
from pynwb import NWBHDF5IO

# Add the Jnwb directory to the Python path to allow imports
sys.path.append(os.path.abspath('Jnwb'))
try:
    import jnwb.core as jnwb_core
except ImportError as e:
    print(f"Error: Could not import the jnwb toolbox. Make sure it's in the workspace.")
    print(f"Import Error: {e}")
    sys.exit(1)

def get_definitive_neuron_counts():
    """
    Uses the jnwb toolbox to iterate through all NWB files and get the
    definitive count of neurons for each specified brain area.
    """
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    if not nwb_files:
        print("Error: No NWB files found in the 'data/' directory.")
        return None

    area_order = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    total_area_counts = defaultdict(int)

    print(f"Found {len(nwb_files)} NWB files to process...")

    for nwb_path in nwb_files:
        print(f"  - Processing {os.path.basename(nwb_path)}...")
        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwbfile = io.read()
                
                # For each area, get the count of units and add to the total
                for area_name in area_order:
                    # The jnwb.core function does the heavy lifting
                    unit_ids = jnwb_core.get_unit_ids_for_area(nwbfile, area_name)
                    total_area_counts[area_name] += len(unit_ids)
        except Exception as e:
            print(f"    -> ERROR processing file {nwb_path}: {e}")
            continue
            
    return total_area_counts

def plot_counts(area_counts, area_order, output_dir):
    """
    Generates and saves the bar and circular plots.
    """
    if not area_counts:
        print("No area counts to plot.")
        return

    labels = area_order
    values = [area_counts.get(area, 0) for area in labels]

    print("\n--- Definitive Neuron Counts Per Area (from Toolbox) ---")
    for area, count in zip(labels, values):
        print(f"{area}: {count}")

    os.makedirs(output_dir, exist_ok=True)
    
    # --- Create and Save Plots ---
    fig_bar = go.Figure(data=[go.Bar(x=labels, y=values, text=values, textposition='auto')])
    fig_bar.update_layout(title_text='Total Unique Neurons per Brain Area (Toolbox Final)', xaxis_title='Brain Area', yaxis_title='Number of Neurons')
    
    fig_polar = go.Figure(data=[go.Barpolar(r=values, theta=labels, text=values, hoverinfo='r+theta')])
    fig_polar.update_layout(title_text='Total Unique Neurons per Area (Circular, Toolbox Final)')

    try:
        fig_bar.write_html(os.path.join(output_dir, "neuron_counts_bar_toolbox.html"))
        fig_bar.write_image(os.path.join(output_dir, "neuron_counts_bar_toolbox.svg"))
        fig_polar.write_html(os.path.join(output_dir, "neuron_counts_circular_toolbox.html"))
        fig_polar.write_image(os.path.join(output_dir, "neuron_counts_circular_toolbox.svg"))
        print(f"\nSuccessfully saved all 4 definitive plot files to {output_dir}")
    except Exception as e:
        print(f"\nAn error occurred while saving the plots: {e}")


def main():
    parser = argparse.ArgumentParser(description="Get and plot definitive neuron counts using the jnwb toolbox.")
    parser.add_argument('--output_dir', type=str, default='figures', help='Directory to save the output plots.')
    args = parser.parse_args()

    # This is a long process, so we run it and then plot
    final_counts = get_definitive_neuron_counts()
    plot_counts(final_counts, ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC'], args.output_dir)

if __name__ == '__main__':
    main()
