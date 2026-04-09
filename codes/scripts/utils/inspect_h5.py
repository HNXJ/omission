import h5py

def inspect_h5py_raw_structure(filepath, max_display_elements=5):
    """
    Recursively inspects a raw HDF5 file (e.g., an NWB file) using h5py,
    printing its group and dataset structure.

    Args:
        filepath (str): The path to the HDF5 file.
        max_display_elements (int): Maximum number of elements to display for small arrays.
    """

    def _print_item(name, obj, indent=0):
        indent_str = '  ' * indent
        if isinstance(obj, h5py.Group):
            # Print only group name; recursive call handles children
            print(f"{indent_str}Group: {name}")
            for key, val in obj.items():
                _print_item(key, val, indent + 1)
        elif isinstance(obj, h5py.Dataset):
            value_info = f"Shape: {obj.shape}, Dtype: {obj.dtype}"
            if obj.size <= max_display_elements and obj.ndim <= 1: # Only display small 1D datasets directly
                try:
                    value_info += f", Value: {obj[()]}"
                except Exception as e:
                    value_info += f" (Error reading value: {e})"
            print(f"{indent_str}Dataset: {name} ({value_info})")
        else:
            print(f"{indent_str}Unknown: {name} (Type: {type(obj).__name__})")

    print(f"\n--- Inspecting Raw HDF5 Structure of: {filepath} ---")
    try:
        with h5py.File(filepath, 'r') as f:
            _print_item(f.name, f, indent=0)
    except Exception as e:
        print(f"Error accessing HDF5 file: {e}")
    print("--- End Raw HDF5 Inspection ---")
