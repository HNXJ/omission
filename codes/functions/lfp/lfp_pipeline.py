import numpy as np
import pandas as pd

def get_signal_conditional(session, area, signal_type='LFP'):
    """Canonical accessor for neural signals."""
    electrodes = session.electrodes.to_dataframe()
    units = session.units.to_dataframe()
    # Mapping peak_channel_id to electrode location needs refinement
    return units[units['quality'] == '1.0']
