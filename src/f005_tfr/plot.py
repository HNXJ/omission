# core
from src.analysis.visualization.lfp_plotting import create_tfr_figure
from src.analysis.io.logger import log

def plot_area_tfrs(results: dict, output_dir: str = "D:/drive/outputs/oglo-8figs/f005"):
    """
    Plots TFR heatmaps for multiple areas.
    """
    for area, res in results.items():
        plotter = create_tfr_figure(
            freqs=res["freqs"], 
            times_ms=res["times"], 
            power=res["tfr"], 
            title=f"Figure 5: {area} Omission TFR",
            area=area
        )
        plotter.save(output_dir, f"fig5_tfr_local_{area}")
