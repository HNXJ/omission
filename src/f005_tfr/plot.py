import os
from src.analysis.visualization.lfp_plotting import create_tfr_figure
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_constants import TIMING_MS
from src.analysis.io.loader import DataLoader

def plot_area_tfrs(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    loader = DataLoader()
    for cond, area_data in results.items():
        onset_ms = loader.get_omission_onset(cond)
        for area, res in area_data.items():
            print(f"[action] Plotting TFR for {area} ({cond})")
            plotter = create_tfr_figure(
                freqs=res["freqs"], 
                times_ms=res["times"], 
                power=res["tfr"], 
                title=f"Figure f005: {area} TFR ({cond})",
                area=area
            )
            
            # Add Sequence Timing Markers shifted by omission onset
            for marker_name, t_val in TIMING_MS.items():
                shifted_t = t_val - onset_ms
                if -1500 <= shifted_t <= 2000:
                    dash_style = "dot" if marker_name.startswith("d") else "dash"
                    plotter.add_xline(shifted_t, marker_name.upper(), color="white", dash=dash_style)

            plotter.add_xline(0, "OMISSION (P2)", color="white", dash="dash")
            plotter.fig.update_xaxes(range=[-2000, 2000])

            # Filename aligned with dashboard expectations
            filename = f"fig5_tfr_{area}"
            plotter.save(output_dir, filename)
            log.progress(f"Saved {filename}.html")
