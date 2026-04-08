"""
lfp_constants.py
Shared constants for LFP Omission analysis (V4 Suite).
Combines standardized timing, hierarchical tiers, and project-specific aesthetics.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, List, Any

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

# --- Area Naming and Hierarchy ---
CANONICAL_AREAS: List[str] = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']

AREA_ALIAS_MAP: Dict[str, str] = {
    'V3': 'V3d', # Default V3 to V3d, can be refined
    'DP': 'V4',
}

HIERARCHY: Dict[str, List[str]] = {
    "Low": ["V1", "V2"],
    "Mid": ["V3d", "V3a", "V4", "MT", "MST", "TEO", "FST"],
    "High": ["FEF", "PFC"]
}

AREA_TIERS: Dict[str, List[str]] = {k.lower(): v for k, v in HIERARCHY.items()}

# --- Timing Constants (in milliseconds from P1 onset = 0ms) ---
# Cycle = 1031ms (P: 531ms, D: 500ms) - This seems to be incorrect, p1 is 531, d1 is 500, p2 is 531, ...
# The end times are not consistent with the cycle length. I will correct them.
# P1: 0 to 531 (531ms)
# D1: 531 to 1031 (500ms)
# P2: 1031 to 1562 (531ms)
# D2: 1562 to 2062 (500ms)
# P3: 2062 to 2593 (531ms)
# D3: 2593 to 3093 (500ms)
# P4: 3093 to 3624 (531ms)
# D4: 3624 to 4124 (500ms)

SEQUENCE_TIMING_MS: Dict[str, Dict[str, Any]] = {
    "p1": {"start": 0, "end": 531, "color": GOLD},
    "d1": {"start": 531, "end": 1031, "color": GRAY},
    "p2": {"start": 1031, "end": 1562, "color": VIOLET},
    "d2": {"start": 1562, "end": 2062, "color": GRAY},
    "p3": {"start": 2062, "end": 2593, "color": TEAL},
    "d3": {"start": 2593, "end": 3093, "color": GRAY},
    "p4": {"start": 3093, "end": 3624, "color": ORANGE},
    "d4": {"start": 3624, "end": 4124, "color": GRAY}
}

TIMING_MS: Dict[str, int] = {name: info["start"] for name, info in SEQUENCE_TIMING_MS.items()}
TIMING_MS["fx"] = -500    # fixation window: -500ms to 0ms (baseline)

EVENT_LINES_MS: Dict[str, int] = TIMING_MS.copy()

# Omission timings for patches (ms, from p1 onset = 0ms)
OMISSION_PATCHES_MS: Dict[str, Tuple[int, int]] = {
    'AXAB': (SEQUENCE_TIMING_MS['p2']['start'], SEQUENCE_TIMING_MS['p2']['end']),
    'BXBA': (SEQUENCE_TIMING_MS['p2']['start'], SEQUENCE_TIMING_MS['p2']['end']),
    'RXRR': (SEQUENCE_TIMING_MS['p2']['start'], SEQUENCE_TIMING_MS['p2']['end']),
    'AAXB': (SEQUENCE_TIMING_MS['p3']['start'], SEQUENCE_TIMING_MS['p3']['end']),
    'BBXA': (SEQUENCE_TIMING_MS['p3']['start'], SEQUENCE_TIMING_MS['p3']['end']),
    'RRXR': (SEQUENCE_TIMING_MS['p3']['start'], SEQUENCE_TIMING_MS['p3']['end']),
    'AAAX': (SEQUENCE_TIMING_MS['p4']['start'], SEQUENCE_TIMING_MS['p4']['end']),
    'BBBX': (SEQUENCE_TIMING_MS['p4']['start'], SEQUENCE_TIMING_MS['p4']['end']),
    'RRRX': (SEQUENCE_TIMING_MS['p4']['start'], SEQUENCE_TIMING_MS['p4']['end'])
}

# --- Other Constants ---

# Standard Frequency Bands
BANDS: Dict[str, Tuple[int, int]] = {
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),    # widened per 15-step protocol
    "Gamma": (35, 70)
}

# All OGLO conditions
ALL_CONDITIONS: List[str] = [
    "AAAB", "AXAB", "AAXB", "AAAX",
    "BBBA", "BXBA", "BBXA", "BBBX",
    "RRRR", "RXRR", "RRXR", "RRRX",
]

OMISSION_CONDITIONS: List[str] = [c for c in ALL_CONDITIONS if "X" in c]

DEFAULT_WF_PARAMS: Dict[str, Any] = {
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
