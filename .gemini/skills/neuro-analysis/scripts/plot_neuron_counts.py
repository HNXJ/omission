
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import argparse
import os

def plot_neuron_counts_from_csv_corrected(csv_path, output_dir):
    """
    Reads the detailed unit CSV file, correctly parses grouped area names,
    calculates the total number of unique neurons per brain area, and
    generates the final bar and circular plots.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return

    unique_units_df = df.drop_duplicates(subset=['session_id', 'probe_id', 'unit_idx'])

    area_order = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
    area_counts = {area: 0.0 for area in area_order}

    for area_str in unique_units_df['area']:
        areas = [a.strip() for a in area_str.split('/')]
        if len(areas) > 1:
            if "V1" in areas and "V2" in areas:
                area_counts['V1'] += 1
                area_counts['V2'] += 1
            elif "V3" in areas and "V4" in areas:
                area_counts['V3d'] += 0.5
                area_counts['V3a'] += 0.5
                area_counts['V4'] += 1
        elif len(areas) == 1:
            area = areas[0]
            if area in area_counts:
                area_counts[area] += 1
    
    final_counts = {k: round(v) for k, v in area_counts.items()}

    labels = area_order
    values = [final_counts[area] for area in labels]

    print("--- Final Corrected Neuron Counts Per Area ---")
    for area, count in zip(labels, values):
        print(f"{area}: {count}")

    os.makedirs(output_dir, exist_ok=True)

    fig_bar = go.Figure(data=[go.Bar(x=labels, y=values, text=values, textposition='auto')])
    fig_bar.update_layout(
        title_text='Total Number of Unique Neurons per Brain Area (Final)',
        xaxis_title='Brain Area',
        yaxis_title='Number of Neurons',
        template='plotly_white'
    )

    fig_polar = go.Figure(data=[go.Barpolar(r=values, theta=labels, text=values, hoverinfo='r+theta')])
    fig_polar.update_layout(title_text='Total Number of Neurons per Area (Circular, Final)', template='plotly_white')

    try:
        fig_bar.write_html(os.path.join(output_dir, "neuron_counts_bar_final.html"))
        fig_bar.write_image(os.path.join(output_dir, "neuron_counts_bar_final.svg"))
        fig_polar.write_html(os.path.join(output_dir, "neuron_counts_circular_final.html"))
        fig_polar.write_image(os.path.join(output_dir, "neuron_counts_circular_final.svg"))
        print(f"\nSuccessfully saved all 4 final plot files to {output_dir}")
    except Exception as e:
        print(f"\nAn error occurred while saving the plots: {e}")

def main():
    parser = argparse.ArgumentParser(description="Plot neuron counts per area from a CSV file.")
    parser.add_argument('--csv_path', type=str, default='checkpoints/omission_units_layered.csv', help='Path to the detailed unit CSV file.')
    parser.add_argument('--output_dir', type=str, default='figures', help='Directory to save the output plots.')
    args = parser.parse_args()
    
    plot_neuron_counts_from_csv_corrected(args.csv_path, args.output_dir)

if __name__ == '__main__':
    main()
