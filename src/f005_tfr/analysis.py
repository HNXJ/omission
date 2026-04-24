import numpy as np
from src.analysis.lfp.lfp_pipeline import run_lfp_spectral_pipeline
from src.analysis.io.logger import log

def analyze_area_tfrs(areas: list, conditions=None):
    if conditions is None:
        conditions = ["AXAB", "AAAB"] 
        
    results = {}
    for cond in conditions:
        print(f"[action] Analyzing TFR family: {cond}")
        results[cond] = {}
        for area in areas:
            print(f"[action] Running LFP pipeline for {area} ({cond})")
            try:
                res = run_lfp_spectral_pipeline(area, cond)
                if res is not None:
                    results[cond][area] = res
            except Exception as e:
                print(f"[error] Failed {area} {cond}: {e}")
    return results
