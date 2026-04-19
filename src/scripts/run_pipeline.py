# core
import sys
import time
from src.analysis.io.logger import log
from src.f001_theory.script import run_f001
from src.f002_psth.script import run_f002
from src.f003_surprise.script import run_f003
from src.f004_coding.script import run_f004
from src.f005_tfr.script import run_f005
from src.f006_band_power.script import run_f006
from src.f007_sfc.script import run_f007
from src.f008_coordination.script import run_f008
from src.f009_individual_sfc.script import run_f009
from src.f010_sfc_delta.script import run_f010
from src.f011_laminar.script import run_f011
from src.f012_mi_matrix.script import run_f012
from src.f013_connectivity_graph.script import run_f013
from src.f014_connectivity_delta.script import run_f014
from src.f015_global_dynamics.script import run_f015
from src.f016_impedance_profiles.script import run_f016

def run_all():
    """
    Executes the comprehensive Omission analytical pipeline sequentially.
    """
    log.progress(f"[action] Initializing Omission Analytical Batch Pipeline...")
    
    start_time = time.time()
    
    # Target directory mapping
    pipeline_steps = [
        ("Figure 1: Theory", run_f001),
        ("Figure 2: PSTH Design", run_f002),
        ("Figure 3: Surprise", run_f003),
        ("Figure 4: Coding", run_f004),
        ("Figure 5: TFR", run_f005),
        ("Figure 6: Band Power", run_f006),
        ("Figure 7: SFC", run_f007),
        ("Figure 8: Coordination", run_f008),
        ("Figure 9: Individual SFC", run_f009),
        ("Figure 10: SFC Delta", run_f010),
        ("Figure 11: Laminar", run_f011),
        ("Figure 12: MI Matrix", run_f012),
        ("Figure 13: Connectivity Graph", run_f013),
        ("Figure 14: Connectivity Delta", run_f014),
        ("Figure 15: Global Dynamics", run_f015),
        ("Figure 16: Impedance", run_f016)
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