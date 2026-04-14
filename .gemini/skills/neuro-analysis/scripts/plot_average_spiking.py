
import numpy as np
import glob
import plotly.graph_objects as go
from scipy.signal.windows import gaussian
import argparse
import os

def get_avg_firing_rate_for_condition(files):
    """
    Calculates the average firing rate across all trials and units for a given list of .npy files.
    """
    kernel = gaussian(100, 20)
    kernel /= np.sum(kernel)
    all_file_averages = []
    for f in files:
        data = np.load(f, mmap_mode='r')
        if data.size == 0 or data.shape[2] != 6000:
            print(f"Skipping file {f} due to invalid shape: {data.shape}")
            continue
        smoothed_data = np.apply_along_axis(lambda x: np.convolve(x, kernel, 'same'), axis=2, arr=data) * 1000
        mean_firing_rate = np.mean(smoothed_data, axis=(0, 1))
        all_file_averages.append(mean_firing_rate)
    if not all_file_averages:
        return None
    grand_average = np.mean(all_file_averages, axis=0)
    return grand_average

def main():
    """
    Main function to parse arguments and generate the plot.
    """
    parser = argparse.ArgumentParser(description="Plot average spiking activity for RRRR and RXRR conditions.")
    parser.add_argument('--data_dir', type=str, default='../assets/data', help='Directory containing the .npy spike data files.')
    parser.add_argument('--output_dir', type=str, default='../../figures', help='Directory to save the output plots.')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    rrrr_path_pattern = os.path.join(args.data_dir, '*-units-*-spk-RRRR.npy')
    rxrr_path_pattern = os.path.join(args.data_dir, '*-units-*-spk-RXRR.npy')
    rrrr_files = glob.glob(rrrr_path_pattern)
    rxrr_files = glob.glob(rxrr_path_pattern)

    print(f"Found {len(rrrr_files)} RRRR files and {len(rxrr_files)} RXRR files in {args.data_dir}")

    print("Processing RRRR files...")
    avg_rrrr = get_avg_firing_rate_for_condition(rrrr_files)
    print("Processing RXRR files...")
    avg_rxrr = get_avg_firing_rate_for_condition(rxrr_files)

    if avg_rrrr is None or avg_rxrr is None:
        print("Could not generate plot because no valid data was found for one or both conditions.")
        return

    fig = go.Figure()
    time_axis = np.linspace(-1000, 5000, 6000)
    fig.add_trace(go.Scatter(x=time_axis, y=avg_rrrr, mode='lines', name='RRRR (Control)'))
    fig.add_trace(go.Scatter(x=time_axis, y=avg_rxrr, mode='lines', name='RXRR (Omission)'))

    event_windows = {
        "p1": (0, 531), "d1": (531, 1031),
        "p2": (1031, 1562), "d2": (1562, 2062),
        "p3": (2062, 2593), "d3": (2593, 3093),
        "p4": (3093, 3624), "d4": (3624, 4124)
    }
    colors = {"p": 'rgba(0, 100, 0, 0.1)', "d": 'rgba(100, 100, 100, 0.1)'}
    for event, (start, end) in event_windows.items():
        fig.add_vrect(x0=start, x1=end, fillcolor=colors[event[0]], line_width=0, annotation_text=event, annotation_position="top left")

    fig.add_vrect(x0=1031, x1=1562, fillcolor='rgba(255, 0, 0, 0.2)', line_width=0,
                  annotation_text="p2 (Omission in RXRR)", annotation_position="bottom left", layer='above')

    fig.update_layout(
        title="Average Firing Rate: RRRR (Control) vs. RXRR (Omission)",
        xaxis_title="Time (ms)",
        yaxis_title="Average Firing Rate (Hz)",
        legend_title="Condition",
        template="plotly_white"
    )

    output_base = os.path.join(args.output_dir, "average_spiking_activity")
    fig.write_html(f"{output_base}.html")
    try:
        fig.write_image(f"{output_base}.svg")
        print(f"Successfully saved plots to {output_base}.html and .svg")
    except Exception as e:
        print(f"Could not save SVG: {e}")

if __name__ == '__main__':
    main()
