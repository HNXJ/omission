# core
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log

def analyze_area_tfrs(areas: list, condition="AXAB"):
    """
    Runs the LFP spectral pipeline for multiple areas.
    """
    results = {}
    for area in areas:
        log.info(f"Running LFP pipeline for {area}")
        res = run_lfp_spectral_pipeline(area, condition)
        if res:
            results[area] = res
    return results
