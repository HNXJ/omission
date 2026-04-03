"""
lfp_constants.py
Standard constants for LFP Omission analysis (V4 Suite).
"""

# Project Aesthetic: Madelane Golden Dark + Violet
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
PINK = "#FF1493"
TEAL = "#00FFCC"
ORANGE = "#FF5E00"
GRAY = "#D3D3D3"

# Gamma-Standard Timing (Sample 1000 = p1 Onset = 0ms)
# Cycle = 1031ms (P: 531ms, D: 500ms)
SEQUENCE_TIMING = {
    "p1": {"start": 0, "end": 531, "color": GOLD},
    "d1": {"start": 531, "end": 1031, "color": GRAY},
    "p2": {"start": 1031, "end": 1562, "color": VIOLET},
    "d2": {"start": 1562, "end": 2062, "color": GRAY},
    "p3": {"start": 2062, "end": 2593, "color": TEAL},
    "d3": {"start": 2593, "end": 3093, "color": GRAY},
    "p4": {"start": 3093, "end": 3624, "color": ORANGE},
    "d4": {"start": 3624, "end": 4124, "color": GRAY}
}

TIMING_MS = {name: info["start"] for name, info in SEQUENCE_TIMING.items()}
TIMING_MS["fx"] = -1000

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
