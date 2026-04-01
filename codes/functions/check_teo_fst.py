
import pynwb
from pynwb import NWBHDF5IO
import pandas as pd

def check_teo_fst_channels():
    nwb_path = 'data/sub-C31o_ses-230818_rec.nwb'
    with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
        nwbfile = io.read()
        units_df = nwbfile.units.to_dataframe()
        electrodes_df = nwbfile.electrodes.to_dataframe()
        
        print(f"Checking Session 230818 for TEO/FST units...")
        
        for idx, unit in units_df.iterrows():
            peak_chan_id = int(float(unit['peak_channel_id']))
            elec = electrodes_df.loc[peak_chan_id]
            raw_label = elec.get('location', elec.get('label', 'unknown'))
            if isinstance(raw_label, bytes): raw_label = raw_label.decode('utf-8')
            
            if "TEO" in raw_label or "FST" in raw_label:
                probe_id = peak_chan_id // 128
                channel_in_probe = peak_chan_id % 128
                print(f"Unit {idx}: Probe {probe_id}, Chan {channel_in_probe}, Label '{raw_label}'")

if __name__ == '__main__':
    check_teo_fst_channels()
