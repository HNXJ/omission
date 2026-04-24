import os
from src.analysis.visualization.lfp_plotting import create_tfr_figure
from src.analysis.io.logger import log

def plot_area_tfrs(results: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for cond, area_data in results.items():
        for area, res in area_data.items():
            print(f"[action] Plotting TFR for {area} ({cond})")
            plotter = create_tfr_figure(
                freqs=res["freqs"], 
                times_ms=res["times"], 
                power=res["tfr"], 
                title=f"Figure f005: {area} TFR ({cond})",
                area=area
            )
            filename = f"f005_tfr_local_{area}_{cond}"
            plotter.save(output_dir, filename)
            log.progress(f"Saved {filename}.html")
