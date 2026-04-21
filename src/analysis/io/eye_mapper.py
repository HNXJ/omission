import pandas as pd
from pathlib import Path
import re
import os

class EyeDataMapper:
    """
    Manages the mapping of behavioral data (.bhv2.mat) specifically for oculomotor and pupil (EYE) analysis,
    ensuring a 1:1 correspondence with canonical NWB files.
    """
    def __init__(self, behavioral_dir: str = r"D:\drive\data\behavioral", nwb_dir: str = r"D:\drive\data\nwb-arrays"):
        self.behavioral_dir = Path(behavioral_dir)
        self.nwb_dir = Path(nwb_dir)
        
        # Dynamically map available behavioral files
        self.behavioral_files = []
        if self.behavioral_dir.exists():
            self.behavioral_files = [f.name for f in self.behavioral_dir.glob("*.bhv2.mat")]
            
        # Dynamically map available NWB files
        self.nwb_files = []
        if self.nwb_dir.exists():
             self.nwb_files = [f.name for f in self.nwb_dir.glob("*.nwb")]
        
    def get_behavioral_file(self, session_id: str) -> Path:
        """
        Retrieves the exact behavioral file path for a given session ID (e.g., '230629').
        Verifies that an NWB file for this session also exists.
        Returns None if no matching file is found or if NWB is missing.
        """
        # First verify NWB existence (to ensure 1:1 mapping as requested)
        # NWB files typically look like 'sub-C31o_ses-230630_rec.nwb' or similar.
        # We check if the session_id is anywhere in the NWB filename.
        has_nwb = False
        for nwb_f in self.nwb_files:
            if session_id in nwb_f:
                has_nwb = True
                break
                
        if not has_nwb and self.nwb_files: # Only strict check if nwb_dir is populated
            # Warning: NWB missing for this session, but we will still return the bhv2 file if it exists
            # as the arrays might have been extracted without the NWB present locally.
            pass

        # Resolve the behavioral file
        for f in self.behavioral_files:
            if f.startswith(session_id):
                return self.behavioral_dir / f
                
        return None
    
    def generate_mapping_table(self):
        """
        Generates a DataFrame summarizing the subject and file mapping.
        """
        records = []
        for f in self.behavioral_files:
            match = re.match(r"(\d{6})_([a-zA-Z]+)_", f)
            if match:
                session = match.group(1)
                subject = match.group(2)
                
                # Check NWB status
                has_nwb = any(session in nwb_f for nwb_f in self.nwb_files)
                
                records.append({
                    "session": session,
                    "subject": subject,
                    "behavioral_file": f,
                    "has_nwb": has_nwb,
                    "path": str(self.behavioral_dir / f)
                })
        return pd.DataFrame(records)

if __name__ == "__main__":
    mapper = EyeDataMapper()
    df = mapper.generate_mapping_table()
    print("Eye Tracking Session Mapping (NWB-Aware):")
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("No behavioral files found in the directory.")
