"""
lfp_constants.py
Shared constants for LFP Omission analysis (V4 Suite).
Combines standardized timing, hierarchical tiers, and project-specific aesthetics.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, List

# Canonical LFP sampling rate — propagated to lfp_tfr, lfp_preproc
FS_LFP: float = 1000.0

# Project Aesthetic: Madelane Golden Dark + Violet
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"
PINK = "#FF1493"
TEAL = "#00FFCC"
ORANGE = "#FF5E00"
GRAY = "#D3D3D3"
WHITE = "#FFFFFF"
SLATE = "#444444"

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
TIMING_MS["fx"] = -500    # fixation window: -500ms to 0ms (baseline)

# Scaffold-compatible event lines
EVENT_LINES_MS: Dict[str, int] = TIMING_MS.copy()

# Standard Frequency Bands
BANDS: Dict[str, Tuple[int, int]] = {
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),    # widened per 15-step protocol
    "Gamma": (35, 70)
}


# Omission timings for patches (ms, from p1 onset = 0ms)
OMISSION_PATCHES = {
    'AXAB': (2031, 2562),
    'BXBA': (2031, 2562),
    'RXRR': (2031, 2562),
    'AAXB': (3062, 3593),
    'BBXA': (3062, 3593),
    'RRXR': (3062, 3593),
    'AAAX': (4093, 4624),
    'BBBX': (4093, 4624),
    'RRRX': (4093, 4624)
}

# All OGLO conditions
ALL_CONDITIONS = [
    "AAAB", "AXAB", "AAXB", "AAAX",
    "BBBA", "BXBA", "BBXA", "BBBX",
    "RRRR", "RXRR", "RRXR", "RRRX",
]

OMISSION_CONDITIONS = [c for c in ALL_CONDITIONS if "X" in c]

# Hierarchical Tiers
HIERARCHY = {
    "Low": ["V1", "V2"],
    "Mid": ["V4", "MT", "MST", "TEO", "FST"],
    "High": ["FEF", "PFC"]
}

AREA_TIERS = {k.lower(): v for k, v in HIERARCHY.items()}

# Targeted 11 Areas for population firing plots
TARGET_AREAS = ['V1', 'V2', 'V3', 'V4', 'MT', 'MST', 'TEO', 'FST', 'DP', 'PFC', 'FEF']

DEFAULT_WF_PARAMS = {
    "window": "hann",
    "nperseg": 256,
    "noverlap": int(0.98 * 256),
}

@dataclass(frozen=True)
class FigureSpec:
    name: str
    title: str
    output_dir: Path
    conditions: List[str]
    sequence: str
    analysis: str
