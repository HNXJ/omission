
import h5py
import os

# Let's use one of the H5 files
H5_PATH = 'data/lfp_by_area_ses-230629.h5'

def inspect_h5_structure(h5_path):
    """Inspects the structure of an HDF5 file."""
    if not os.path.exists(h5_path):
        print(f"Error: H5 file not found at {h5_path}")
        return

    print(f"Inspecting H5 file: {h5_path}")
    try:
        with h5py.File(h5_path, 'r') as f:
            print("Keys at root level:", list(f.keys()))
            
            # Let's assume the structure is area/condition/data
            # and explore the first area
            if f.keys():
                first_area = list(f.keys())[0]
                print(f"\n--- Exploring Area: {first_area} ---")
                
                area_group = f[first_area]
                print(f"Keys under '{first_area}':", list(area_group.keys()))

                # Explore the first condition under that area
                if area_group.keys():
                    first_cond = list(area_group.keys())[0]
                    print(f"\n--- Exploring Condition: {first_cond} under {first_area} ---")
                    
                    cond_dataset = area_group[first_cond]
                    print(f"Dataset '{first_cond}' is a of type: {type(cond_dataset)}")
                    if isinstance(cond_dataset, h5py.Dataset):
                        print("Shape of the dataset:", cond_dataset.shape)
                        print("Data type:", cond_dataset.dtype)
                        # print("First few values:", cond_dataset[:2, :5]) # Look at a small slice
                    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    inspect_h5_structure(H5_PATH)
