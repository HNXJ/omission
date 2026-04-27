import re
import sys

def check_file(path):
    print(f"Checking: {path}")
    try:
        content = open(path, 'r', errors='ignore').read()
    except Exception as e:
        print(f"Error reading: {e}")
        return

    # Literal NaN (unquoted)
    # Looking for NaN not preceded by " and not followed by "
    unquoted_nan = re.search(r'(?<![\"\w])NaN(?![\"\w])', content)
    quoted_nan = re.search(r'\"[^\"]*NaN[^\"]*\"', content)
    
    print(f"Unquoted NaN found: {unquoted_nan is not None}")
    if unquoted_nan:
        idx = unquoted_nan.start()
        print(f"  Snippet: ...{content[max(0, idx-50):idx+50]}...")
    
    # Check for Infinity too
    unquoted_inf = re.search(r'(?<![\"\w])Infinity(?![\"\w])', content)
    print(f"Unquoted Infinity found: {unquoted_inf is not None}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_file(sys.argv[1])
