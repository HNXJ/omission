
import pynwb
from pynwb import NWBHDF5IO
import os

def inspect_nwb_file_deeper(session_id):
    """
    Reads an NWB file and performs a deeper inspection of its metadata
    to find the probe-to-area mapping.
    """
    nwb_file_path = f'data/sub-V198o_ses-{session_id}_rec.nwb'
    
    if not os.path.exists(nwb_file_path):
        print(f"NWB file not found at: {nwb_file_path}")
        return

    print(f"--- Deeper inspection of NWB file: {nwb_file_path} ---")

    try:
        with NWBHDF5IO(nwb_file_path, 'r') as io:
            nwbfile = io.read()
            
            print("\n--- Session Description ---")
            print(nwbfile.session_description)

            print("\n--- Electrode Groups (Probes) Details ---")
            if not nwbfile.electrode_groups:
                print("No Electrode Groups found.")
            for group_name, group in nwbfile.electrode_groups.items():
                print(f"\nGroup Name: {group_name}")
                print(f"  Description: {group.description}")
                print(f"  Location: {group.location}")
                print(f"  Device: {group.device.name}")

            print("\n--- Devices ---")
            if not nwbfile.devices:
                print("No Devices found.")
            for device_name, device in nwbfile.devices.items():
                 print(f"\nDevice Name: {device_name}")
                 print(device)
                 
    except Exception as e:
        print(f"\nAn error occurred while reading the NWB file: {e}")
        print("Please ensure the 'pynwb' library is installed (`pip install pynwb`).")

def main():
    session_to_inspect = '230629'
    inspect_nwb_file_deeper(session_to_inspect)

if __name__ == '__main__':
    main()
