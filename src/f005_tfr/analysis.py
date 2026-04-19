# core
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_constants import OMISSION_CONDITIONS

def analyze_area_tfrs(areas: list, conditions=None):
    """
    Runs the LFP spectral pipeline for multiple areas and conditions.
    """
    if conditions is None:
        conditions = ["AXAB", "AAXB", "AAAX"] # Primary families
        
    results = {}
    for cond in conditions:
        log.info(f"Analyzing TFR family: {cond}")
        results[cond] = {}
        for area in areas:
            log.info(f"Running LFP pipeline for {area} ({cond})")
            res = run_lfp_spectral_pipeline(area, cond)
            if res:
                results[cond][area] = res
    return results
