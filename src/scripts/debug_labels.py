import re
import sys

def check_labels(path):
    print(f"Checking: {path}")
    content = open(path, 'r', errors='ignore').read()
    
    # 1. Title
    has_title = re.search(r'"title":\s*\{[^}]*"text":\s*"[^"]+"', content) is not None
    print(f"Has Title: {has_title}")
    if not has_title:
        # Show title snippet
        match = re.search(r'"title":\s*\{', content)
        if match:
            print(f"  Title Snippet: {content[match.start():match.start()+100]}")

    # 2. XAxis
    has_xaxis = re.search(r'"xaxis\d*":\s*\{[^}]*"title":\s*\{[^}]*"text":\s*"[^"]+"', content) is not None
    print(f"Has XAxis: {has_xaxis}")
    if not has_xaxis:
        match = re.search(r'"xaxis":\s*\{', content)
        if match:
            print(f"  XAxis Snippet: {content[match.start():match.start()+200]}")

    # 3. YAxis
    has_yaxis = re.search(r'"yaxis\d*":\s*\{[^}]*"title":\s*\{[^}]*"text":\s*"[^"]+"', content) is not None
    print(f"Has YAxis: {has_yaxis}")

if __name__ == "__main__":
    check_labels(sys.argv[1])
