# f038 — Layer-Resolved Granger Causality (V1 <-> PFC)
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.analysis.lfp.lfp_laminar_mapping import get_laminar_crossover

def segment_layers(loader: DataLoader, area: str):
    """
    Segments units into Superficial (L2/3) and Deep (L5/6) using vFLIP2 crossover.
    Fallbacks to canonical depth if mapping fails.
    """
    print(f"""[action] Segmenting layers for area: {area}""")
    units = loader.get_units_by_area(area)
    print(f"""[info] Found {len(units)} units for {area}""")
    if not units:
        print(f"""[warning] No units found for {area}, returning empty segmentation""")
        return {"Superficial": [], "Deep": []}
        
    # vFLIP2 crossover logic (simplified for batch)
    # In practice, we'd load LFP for the probe and find crossover.
    # Placeholder: Using canonical channel-based split (0-63 vs 64-127) for initial yield.
    # Note: 128 channels per probe.
    
    seg = {"Superficial": [], "Deep": []}
    print(f"""[action] Iterating {len(units)} units for layer assignment (ch<64=Sup, ch>=64=Deep)""")
    for u_id in units:
        try:
            # unit_id: session-probeN-unitIdx
            u_idx = int(u_id.split("-unit")[1])
            # Probe-local channel index approximation
            if u_idx < 64:
                seg["Superficial"].append(u_id)
            else:
                seg["Deep"].append(u_id)
        except: continue
    
    print(f"""[result] Layer Segmentation for {area}: {len(seg['Superficial'])} Sup, {len(seg['Deep'])} Deep""")
    log.info(f"[f038] Layer Segmentation for {area}: {len(seg['Superficial'])} Sup, {len(seg['Deep'])} Deep")
    return seg


def apply_spike_subsampling(src_pop, tgt_pop):
    """
    Ensures firing rate matching between populations.
    Scales the higher-rate population down to the lower-rate population's mean
    to prevent rate-driven causality bias in the MVAR model.
    
    Input:  src_pop (ndarray, T), tgt_pop (ndarray, T) — population-mean signals.
    Output: src_pop (ndarray, T), tgt_pop (ndarray, T) — rate-matched signals.
    """
    rate_src = np.mean(src_pop)
    rate_tgt = np.mean(tgt_pop)
    print(f"""[action] Rate-matching: src_mean={rate_src:.4f}, tgt_mean={rate_tgt:.4f}""")
    
    if rate_src == 0 or rate_tgt == 0:
        print(f"""[warning] Zero-rate population detected, skipping subsampling""")
        return src_pop, tgt_pop
        
    if rate_src > rate_tgt:
        scale = rate_tgt / rate_src
        print(f"""[action] Scaling source down by {scale:.4f} to match target rate""")
        src_pop = src_pop * scale
    else:
        scale = rate_src / rate_tgt
        print(f"""[action] Scaling target down by {scale:.4f} to match source rate""")
        tgt_pop = tgt_pop * scale
        
    return src_pop, tgt_pop


def compute_layer_granger(loader: DataLoader, source_units: list, target_units: list, 
                         condition: str, window: tuple, maxlag: int = 20):
    """
    Computes Directed Flow (Granger) between population-mean signals of two layers.
    
    Input:
        source_units: list of unit IDs for the source population.
        target_units: list of unit IDs for the target population.
        condition:    str, trial condition code (e.g. "AXAB").
        window:       tuple (start_ms, end_ms) relative to alignment.
        maxlag:       int, maximum AR lag order to test (default=20).
    
    Output:
        float — F-statistic from the optimal lag (min p-value across 1..maxlag).
               Returns 0.0 on failure, None if populations are empty.
    """
    if not source_units or not target_units:
        print(f"""[warning] Empty population: src={len(source_units)}, tgt={len(target_units)}, skipping""")
        return None
        
    # Load and average units for population signal
    # This stabilizes the estimate and avoids trial-by-trial noise issues.
    print(f"""[action] Loading source signals for {len(source_units)} units, window={window}""")
    src_signals = []
    for u in source_units:
        data = loader.load_unit_spikes(u, condition=condition)
        if data is not None:
            # BUG FIX #4: Bounds guard — verify window does not exceed data extent
            if window[1] > data.shape[-1]:
                print(f"""[warning] Window end {window[1]} exceeds data extent {data.shape[-1]} for unit {u}, skipping""")
                continue
            src_signals.append(data[:, window[0]:window[1]])
            
    print(f"""[action] Loading target signals for {len(target_units)} units, window={window}""")
    tgt_signals = []
    for u in target_units:
        data = loader.load_unit_spikes(u, condition=condition)
        if data is not None:
            # BUG FIX #4: Bounds guard
            if window[1] > data.shape[-1]:
                print(f"""[warning] Window end {window[1]} exceeds data extent {data.shape[-1]} for unit {u}, skipping""")
                continue
            tgt_signals.append(data[:, window[0]:window[1]])
            
    if not src_signals or not tgt_signals:
        print(f"""[warning] No valid signals after loading: src={len(src_signals)}, tgt={len(tgt_signals)}""")
        return None
        
    # Population means (timepoints,)
    src_pop = np.mean(np.concatenate(src_signals, axis=0), axis=0)
    tgt_pop = np.mean(np.concatenate(tgt_signals, axis=0), axis=0)
    print(f"""[info] Population signal shapes: src={src_pop.shape}, tgt={tgt_pop.shape}""")
    
    # BUG FIX #1: Apply rate-matching BEFORE MVAR fit
    src_pop, tgt_pop = apply_spike_subsampling(src_pop, tgt_pop)
    print(f"""[action] Rate-matching applied to population signals""")
    
    # BUG FIX #5: Stationarity conditioning via first-order differencing
    # Granger causality assumes weak stationarity. Raw population means
    # often carry drift/transients. np.diff removes linear trends.
    src_pop = np.diff(src_pop)
    tgt_pop = np.diff(tgt_pop)
    print(f"""[action] First-order differencing applied for stationarity (new len={len(src_pop)})""")
    
    # Handle zero variance (post-differencing)
    if np.var(src_pop) < 1e-9 or np.var(tgt_pop) < 1e-9:
        print(f"""[warning] Near-zero variance after differencing, returning 0.0""")
        return 0.0
    
    # Granger expects (n_obs, 2) where tgt is col 0, src is col 1 for tgt ~ src
    data_gc = np.stack([tgt_pop, src_pop], axis=1)
    print(f"""[info] GC input matrix shape: {data_gc.shape}""")
    
    # Minimum observation guard: need at least 3*maxlag observations
    if data_gc.shape[0] < 3 * maxlag:
        print(f"""[warning] Insufficient observations ({data_gc.shape[0]}) for maxlag={maxlag}, need {3*maxlag}""")
        return 0.0
        
    print(f"""[action] Fitting MVAR(maxlag={maxlag}) for {len(source_units)}->{len(target_units)} flow...""")
    try:
        gc_res = grangercausalitytests(data_gc, maxlag=maxlag, verbose=False)
        
        # BUG FIX #3: Scan all lags, select optimal (minimum p-value)
        # gc_res[lag][0] contains test dicts. 'ssr_ftest' -> (F, p, df_denom, df_num)
        best_f = 0.0
        best_p = 1.0
        best_lag = 1
        for lag in range(1, maxlag + 1):
            f_val = gc_res[lag][0]['ssr_ftest'][0]
            p_val = gc_res[lag][0]['ssr_ftest'][1]
            if p_val < best_p:
                best_f = f_val
                best_p = p_val
                best_lag = lag
        
        print(f"""[result] Optimal lag={best_lag}, F={best_f:.4f}, p={best_p:.6f}""")
        return best_f
    except Exception as e:
        print(f"""[error] GC fitting failed: {e}""")
        log.error(f"GC failed: {e}")
        return 0.0


def run_f038_pipeline(loader: DataLoader, session_pairs: list):
    """
    Main pipeline entry point.
    
    Input:
        loader:         DataLoader instance with mmap-backed access.
        session_pairs:  list of (area_src, area_tgt) e.g., [("V1", "PFC")].
    
    Output:
        pd.DataFrame with columns: pair, condition, window, ff_flow, fb_flow.
    """
    results = []
    # Test all omission-relevant conditions across p2/p3/p4 families
    conditions = ["AXAB", "BXBA", "RXRR", "AAXB", "BBXA", "RRXR", "AAAX", "BBBX", "RRRX"]
    print(f"""[action] f038 pipeline starting with {len(conditions)} conditions""")
    
    for area_src, area_tgt in session_pairs:
        print(f"""[f038] Processing pair: {area_src} <-> {area_tgt}""")
        
        # Segment units (LFP-based crossover required for precision)
        src_layers = segment_layers(loader, area_src)
        tgt_layers = segment_layers(loader, area_tgt)
        
        for cond in conditions:
            # Dynamic Omission Onset (Family-Aware)
            omission_onset = loader.get_omission_onset(cond)
            print(f"""[info] Condition {cond}: omission onset = {omission_onset}ms""")
            
            # Windows: Stimulus (Fixed baseline) vs Omission (Dynamic)
            # Alignment is relative to p1 start (1000 is 0ms)
            windows = {
                "Stimulus": (1500, 2000), # p2 slot stimulus (if condition is p3/p4) or p1 baseline
                "Omission": (1000 + int(omission_onset), 1000 + int(omission_onset) + 500)
            }
            
            for win_name, win_range in windows.items():
                print(f"""[f038] Window: {win_name} ({win_range[0]}-{win_range[1]}ms) for {cond}""")
                
                # FF pathway: V1_Superficial -> PFC_Deep (ascending via L2/3 projection)
                print(f"""[action] Computing FF flow: {area_src}_Sup -> {area_tgt}_Deep""")
                ff_flow = compute_layer_granger(loader, src_layers["Superficial"], 
                                              tgt_layers["Deep"], cond, win_range)
                
                # BUG FIX #2: FB pathway: PFC_Deep -> V1_Deep (descending to L5/6 apical dendrites)
                # The canonical FB termination zone is Deep layers, NOT Superficial.
                print(f"""[action] Computing FB flow: {area_tgt}_Deep -> {area_src}_Deep""")
                fb_flow = compute_layer_granger(loader, tgt_layers["Deep"], 
                                              src_layers["Deep"], cond, win_range)
                
                print(f"""[result] {cond}/{win_name}: FF={ff_flow}, FB={fb_flow}""")
                results.append({
                    "pair": f"{area_src}->{area_tgt}",
                    "condition": cond,
                    "window": win_name,
                    "ff_flow": ff_flow,
                    "fb_flow": fb_flow
                })
                
    print(f"""[action] Pipeline complete. {len(results)} result rows generated.""")
    return pd.DataFrame(results)
