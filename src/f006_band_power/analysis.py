# core
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log

def analyze_band_dynamics(areas: list, condition="AXAB"):
    """
    Computes band-specific power dynamics for multiple areas.
    """
    results = {}
    for area in areas:
        log.info(f"Running Band pipeline for {area}")
        res = run_lfp_spectral_pipeline(area, condition)
        if res:
            results[area] = res
    return results
