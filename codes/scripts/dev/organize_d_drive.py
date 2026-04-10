# Local-only
# This script is for local development and contains machine-specific paths and configurations.

import os
import shutil

ROOT_DIR = 'D:/'
DATA_EXTENSIONS = ('.npy', '.nwb', '.mat', '.hd5', '.h5')

def organize_data_files(root):
    print(f"Starting organization of data files in {root}...")
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip git repositories and their contents
        if '.git' in dirnames:
            print(f"  Skipping Git repository: {dirpath}")
            dirnames.remove('.git')
            continue
            
        # Skip if we are already inside a 'data' folder
        if os.path.basename(dirpath).lower() == 'data':
            continue
            
        # Find matching data files in the current folder
        data_files = [f for f in filenames if f.lower().endswith(DATA_EXTENSIONS)]
        
        if data_files:
            data_subdir = os.path.join(dirpath, 'data')
            
            # Create data folder if it doesn't exist
            if not os.path.exists(data_subdir):
                try:
                    os.makedirs(data_subdir)
                    print(f"  Created: {data_subdir}")
                except Exception as e:
                    print(f"  Error creating {data_subdir}: {e}")
                    continue
            
            # Move files
            for f in data_files:
                src = os.path.join(dirpath, f)
                dst = os.path.join(data_subdir, f)
                
                # Avoid moving if destination already exists (to prevent overwriting)
                if os.path.exists(dst):
                    print(f"  Warning: {f} already exists in {data_subdir}. Skipping.")
                    continue
                    
                try:
                    shutil.move(src, dst)
                    print(f"  Moved: {f} -> data/")
                except Exception as e:
                    print(f"  Error moving {f}: {e}")

if __name__ == "__main__":
    # We only process top-level non-system folders to be safe
    try:
        entries = os.listdir(ROOT_DIR)
    except PermissionError as e:
        print(f"Permission denied accessing root: {e}")
        entries = []

    for entry in entries:
        full_path = os.path.join(ROOT_DIR, entry)
        # Skip system files/folders and known large non-target areas if necessary
        if os.path.isdir(full_path) and not entry.startswith('$') and entry != 'System Volume Information':
            organize_data_files(full_path)
