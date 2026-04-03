"""
lfp_constants.py
Standard constants for LFP Omission analysis (V4 Suite).
"""

# Project Aesthetic: Madelane Golden Dark + Violet
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
PINK = "#FF1493"  # Omission Highlight

# Gamma-Standard Timing (Sample 1000 = p1 Onset)
TIMING_MS = {
    "fx": -1000, "p1": 0, "d1": 531, 
    "p2": 1031, "d2": 1562, 
    "p3": 2062, "d3": 2593, 
    "p4": 3093, "d4": 3624
}

# Standard Frequency Bands
BANDS = {
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (15, 25),
    "Gamma": (35, 70)
}

# Hierarchical Tiers
HIERARCHY = {
    "Low": ["V1", "V2"],
    "Mid": ["V4", "MT", "MST", "TEO", "FST"],
    "High": ["FEF", "PFC"]
}
