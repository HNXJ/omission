# core
import sys
import time
from src.analysis.io.logger import log

# Figure Imports (Canonical f001-f046)
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
from src.f012_csd_profiling.script import run_f012
from src.f013_rhythmic_evolution.script import run_f013
from src.f014_spiking_granger.script import run_f014
from src.f015_spectral_granger.script import run_f015
from src.f016_impedance_profiles.script import run_f016
from src.f017_prediction_errors.script import run_f017
from src.f018_ghost_signals.script import run_f018
from src.f019_pac_analysis.script import run_f019
from src.f020_effective_connectivity.script import run_f020
from src.f021_pupil_decoding.script import run_f021
from src.f022_dimensionality_reduction.script import run_f022
from src.f023_spectral_fingerprints.script import run_f023
from src.f024_fano_factor.script import run_f024
from src.f025_state_decoding.script import run_f025
from src.f026_state_latency.script import run_f026
from src.f027_identity_coding.script import run_f027
from src.f028_state_manifolds.script import run_f028
from src.f029_info_bottleneck.script import run_f029
from src.f030_recurrence_dynamics.script import run_f030
from src.f031_spike_phase_locking.script import run_f031
from src.f032_spike_triggered_average.script import run_f032
from src.f033_spike_field_coherence.script import run_f033
from src.f034_pev_analysis.script import run_f034
from src.f035_deviance_scaling.script import run_f035
from src.f036_interneuron_dynamics.script import run_f036
from src.f039_spike_field_coherence.script import run_f039
from src.f040_onset_latency.script import run_f040
from src.f044_laminar_pac.script import run_f044
from src.f045_laminar_coherence.script import run_f045
from src.f046_state_space_trajectories.script import run_f046

def run_all():
    """
    Executes the comprehensive Omission analytical pipeline sequentially.
    """
    log.progress(f"[action] Initializing Omission Analytical Batch Pipeline (f001-f046)...")
    
    start_time = time.time()
    
    pipeline_steps = [
        ("Figure 1: Theory", run_f001),
        ("Figure 2: PSTH", run_f002),
        ("Figure 3: Surprise", run_f003),
        ("Figure 4: Coding", run_f004),
        ("Figure 5: TFR", run_f005),
        ("Figure 6: Band Power", run_f006),
        ("Figure 7: SFC", run_f007),
        ("Figure 8: Coordination", run_f008),
        ("Figure 9: Individual SFC", run_f009),
        ("Figure 10: Delta SFC", run_f010),
        ("Figure 11: Laminar Alignment", run_f011),
        ("Figure 12: CSD Profiling", run_f012),
        ("Figure 13: Rhythmic Evolution", run_f013),
        ("Figure 14: Spiking Granger", run_f014),
        ("Figure 15: Spectral Granger", run_f015),
        ("Figure 16: Impedance Profiles", run_f016),
        ("Figure 17: Prediction Errors", run_f017),
        ("Figure 18: Ghost Signals", run_f018),
        ("Figure 19: PAC Analysis", run_f019),
        ("Figure 20: Effective Connectivity", run_f020),
        ("Figure 21: Pupil Decoding", run_f021),
        ("Figure 22: Dimensionality Reduction", run_f022),
        ("Figure 23: Spectral Fingerprints", run_f023),
        ("Figure 24: Fano Factor", run_f024),
        ("Figure 25: State Decoding", run_f025),
        ("Figure 26: State Latency", run_f026),
        ("Figure 27: Identity Coding", run_f027),
        ("Figure 28: State Manifolds", run_f028),
        ("Figure 29: Info Bottleneck", run_f029),
        ("Figure 30: Recurrence Dynamics", run_f030),
        ("Figure 31: Spike Phase Locking", run_f031),
        ("Figure 32: Spike Triggered Average", run_f032),
        ("Figure 33: Spike Field Coherence", run_f033),
        ("Figure 34: PEV Analysis", run_f034),
        ("Figure 35: Deviance Scaling", run_f035),
        ("Figure 36: Interneuron Dynamics", run_f036),
        ("Figure 39: Spike-Field Coherence (PPC)", run_f039),
        ("Figure 40: Population Sync Index", run_f040),
        ("Figure 44: Laminar PAC", run_f044),
        ("Figure 45: Laminar Coherence", run_f045),
        ("Figure 46: State-Space Trajectories", run_f046),
    ]
    
    for name, func in pipeline_steps:
        log.progress(f"--------------------------------------------------")
        log.progress(f"[action] STARTING: {name}")
        try:
            func()
            log.progress(f"[action] SUCCESS: {name}")
        except Exception as e:
            log.error(f"[action] FAILED: {name} - {e}")
            
    elapsed = time.time() - start_time
    log.progress(f"--------------------------------------------------")
    log.progress(f"[action] Pipeline complete in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    run_all()
