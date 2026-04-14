#!/usr/bin/env python3
"""
Spectral Integrity Checker
Validates that LFP power distributions are within physiological norms.
Detects dead channels, artifacts, or signal dropout in real-time.
"""
from __future__ import annotations
import numpy as np

def validate_powers(powers: dict[str, float], session_id: str, area: str) -> bool:
    """
    Checks if band powers are within reasonable dB ranges.
    Returns True if valid, False if suspicious.
    """
    # Thresholds (dB relative to 1uV^2)
    # Typical LFP power ranges from 0 to 60 dB depending on area/state
    LIMITS = {
        "Theta": (0.1, 1000.0),
        "Alpha": (0.1, 1000.0),
        "Beta": (0.1, 500.0),
        "Gamma": (0.1, 300.0)
    }
    
    for band, val in powers.items():
        if band not in LIMITS: continue
        low, high = LIMITS[band]
        if val < low:
            print(f"[Warning] {session_id} | {area} | {band} power TOO LOW ({val:.2f}) - Possible dead channel.")
            return False
        if val > high:
            print(f"[Warning] {session_id} | {area} | {band} power TOO HIGH ({val:.2f}) - Possible artifact.")
            return False
            
    return True

def check_flatline(trace: np.ndarray, threshold: float = 1e-9) -> bool:
    """Detects digitizer flatlining or zeroed-out signals."""
    v = np.var(trace)
    return v < threshold
