# core
import numpy as np
import pandas as pd
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

class LaminarMapper:
    """
    Canonical mapper for cortical laminar identity.
    Probe-specific channel-to-depth mapping.
    """
    def __init__(self, probe_type: str = "128-ch"):
        # Placeholder mapping: Standardized depth indices
        # 128 channels, mapped to 0-128 (assuming linear probe)
        self.depth_map = {
            "Superficial": (0, 40), # ~0-400um
            "L4": (40, 70),         # ~400-700um
            "Deep": (70, 128)       # ~700-1280um
        }

    def get_layer(self, channel_idx: int):
        for layer, (start, end) in self.depth_map.items():
            if start <= channel_idx < end:
                return layer
        return "Unknown"

def map_units_to_layers(unit_metrics: pd.DataFrame, probe_info: dict):
    """
    Maps units to layers based on peak channel.
    """
    mapper = LaminarMapper()
    unit_metrics["layer"] = unit_metrics["peak_channel"].apply(mapper.get_layer)
    return unit_metrics
