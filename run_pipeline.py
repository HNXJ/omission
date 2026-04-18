# core
import sys
import time
from src.core.logger import log
from src.figures import (
    fig1_theory, fig2_psth, fig3_surprise, fig4_coding,
    fig5_tfr, fig6_band_power, fig7_sfc, fig8_coordination,
    fig9_individual_sfc, fig10_sfc_delta, fig11_laminar
)

def run_all():
    """
    Executes the comprehensive Omission 8-Figure Pipeline sequentially.
    """
    log.progress(f"[action] Initializing Omission Analytical Batch Pipeline...")
    
    start_time = time.time()
    
    # Target directory mapping
    pipeline_steps = [
        ("Figure 1: Predictive Coding Theory", fig1_theory.generate_figure_1),
        ("Figure 2: Canonical PSTHs", fig2_psth.generate_figure_2),
        ("Figure 3: Surprise Latencies", fig3_surprise.generate_figure_3),
        ("Figure 4: Identity Coding", fig4_coding.generate_figure_4),
        ("Figure 5: TFR Spectrograms", fig5_tfr.generate_figure_5),
        ("Figure 6: Band Power Dynamics", fig6_band_power.generate_figure_6),
        ("Figure 7: Spike-Field Coupling", fig7_sfc.generate_figure_7),
        ("Figure 8: Cross-Area Coordination", fig8_coordination.generate_figure_8),
        ("Figure 9: Individual SFC (PLV)", fig9_individual_sfc.generate_figure_9),
        ("Figure 10: SFC Delta Contrast", fig10_sfc_delta.generate_figure_10),
        ("Figure 11: Laminar Profiles", fig11_laminar.generate_laminar_figure_11),
    ]
    
    for name, func in pipeline_steps:
        log.progress(f"--------------------------------------------------")
        log.progress(f"[action] STARTING: {name}")
        try:
            func()
            log.progress(f"[action] SUCCESS: {name}")
        except Exception as e:
            log.error(f"[action] FAILED: {name} - {e}")
            sys.exit(1)
            
    elapsed = time.time() - start_time
    log.progress(f"--------------------------------------------------")
    log.progress(f"[action] Pipeline complete in {elapsed:.2f} seconds.")
    log.progress(f"All outputs generated in D:/drive/outputs/oglo-8figs/")

if __name__ == "__main__":
    run_all()