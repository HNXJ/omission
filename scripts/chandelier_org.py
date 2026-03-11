import os
import shutil
import sys

def organize_chandelier(root_dir):
    """
    Enforces the 'Chandelier' organization rule:
    - Max 5 subfolders per directory (6 for root).
    - Every directory gets a 'misc' folder for loose files.
    - 'hnxj-gemini' is exempt.
    """
    print(f"📐 Enforcing Chandelier Structure on: {root_dir}")
    
    # Standard Pillars for root
    ROOT_LIMIT = 6
    SUB_LIMIT = 5
    EXEMPT = ["hnxj-gemini", ".git", "__pycache__"]

    def process_dir(current_path, is_root=False):
        # 1. Ensure 'misc' exists
        misc_path = os.path.join(current_path, "misc")
        if not os.path.exists(misc_path):
            os.makedirs(misc_path)

        # 2. Archive loose files to local misc
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isfile(item_path):
                # Don't move hidden files or the content map
                if not item.startswith('.') and item != "workspace_content.md":
                    shutil.move(item_path, os.path.join(misc_path, item))

        # 3. Handle folder limit
        folders = [f for f in os.listdir(current_path) 
                   if os.path.isdir(os.path.join(current_path, f)) 
                   and f != "misc" 
                   and f not in EXEMPT]
        
        limit = ROOT_LIMIT if is_root else SUB_LIMIT
        
        if len(folders) > limit:
            print(f"  ⚠️ Folder limit exceeded in {current_path} ({len(folders)} folders). Merging excess into misc/...")
            # Sort folders to keep the first 'limit' ones
            folders.sort()
            excess_folders = folders[limit:]
            for f in excess_folders:
                shutil.move(os.path.join(current_path, f), os.path.join(misc_path, f))

        # 4. Recursively process subfolders (except misc and exempt)
        remaining_folders = [f for f in os.listdir(current_path) 
                             if os.path.isdir(os.path.join(current_path, f)) 
                             and f != "misc" 
                             and f not in EXEMPT]
        
        for f in remaining_folders:
            process_dir(os.path.join(current_path, f), is_root=False)

    process_dir(root_dir, is_root=True)
    print("✨ Chandelier reorganization complete.")

if __name__ == "__main__":
    target = "/Users/hamednejat/workspace"
    organize_chandelier(target)
