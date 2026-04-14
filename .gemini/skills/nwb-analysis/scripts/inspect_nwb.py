import pynwb
import sys
from pynwb import NWBHDF5IO

def inspect_nwb(file_path):
    try:
        with NWBHDF5IO(file_path, 'r') as io:
            nwbfile = io.read()
            print(f"File: {file_path}")
            print(f"Session: {nwbfile.session_description}")
            
            # Check Units
            if nwbfile.units:
                print(f"Units found: {len(nwbfile.units)}")
            else:
                print("No Units table found.")
            
            # Check Electrical Series
            for mod in nwbfile.processing.values():
                for interface in mod.data_interfaces.values():
                    if isinstance(interface, (pynwb.ecephys.LFP, pynwb.ecephys.ElectricalSeries)):
                        print(f"Ecephys Interface: {interface.name}")

            # Check Behavior
            if 'behavior' in nwbfile.processing:
                print("Behavioral data found.")
    except Exception as e:
        print(f"Error inspecting NWB file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_nwb.py <path_to_nwb>")
        sys.exit(1)
    inspect_nwb(sys.argv[1])
