# core
from src.analysis.io.logger import log

def get_theory_schematic_data():
    """
    Returns the conceptual parameters for the theory schematic.
    """
    log.action("Providing theoretical schematic metadata")
    return {
        "layers": {
            "L23": {"type": "Prediction Error", "oscillation": "Gamma", "color": "#CFB87C"},
            "L56": {"type": "Internal Prediction", "oscillation": "Alpha/Beta", "color": "#9400D3"}
        }
    }
