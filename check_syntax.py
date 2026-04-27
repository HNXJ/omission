import os
import traceback

def check_plots():
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file == "plot.py" or file == "plotting.py":
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        compile(f.read(), path, "exec")
                except SyntaxError as e:
                    print(f"SYNTAX ERROR in {path}: {e}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    print("Checking syntax in all plots...")
    check_plots()
    print("Syntax check complete.")
