import requests
import sys
import time
import json
import os
import platform

# --- Configuration ---
API_URL = "http://10.32.133.50:4474/v1/chat/completions"
API_KEY = "sk-lm-AwTB4ioL:AlYs5lGxRzFajT2wjPxp"
MODEL_NAME = "qwen3.5-35b"
TIMEOUT = 600  

# CRITICAL: Hard cap to prevent segfaults on M3 Max
# Standard LM Studio default is often 32k or 64k. Adjust this to match your UI setting!
MAX_CONTEXT_TOKENS = 64000 

def estimate_tokens(text):
    """Rough estimation of tokens (4 chars/token)."""
    return len(text) // 4

def call_qwen(prompt, system_prompt="You are a senior neuroscience and ML expert assistant. CRITICAL: Always end your response with a 3-sentence 'STATE_COMPRESSION' summary."):
    """Robust API client with strict context guards."""
    
    prompt_tokens = estimate_tokens(prompt)
    system_tokens = estimate_tokens(system_prompt)
    total_tokens = prompt_tokens + system_tokens
    
    print(f"\n[Context Check] Prompt: ~{prompt_tokens} | System: ~{system_tokens} | Total: ~{total_tokens} (Limit: {MAX_CONTEXT_TOKENS})")

    if total_tokens > MAX_CONTEXT_TOKENS:
        print(f"\n[CRITICAL WARNING] Prompt exceeds safety limit ({total_tokens} > {MAX_CONTEXT_TOKENS}).")
        print("To prevent a Segmentation Fault on the Office Mac, I will truncate the prompt.")
        # Truncate keeping the most recent part (end of prompt)
        chars_to_keep = MAX_CONTEXT_TOKENS * 4
        prompt = "... [TRUNCATED] ... " + prompt[-chars_to_keep:]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    current_host = platform.node()
    print(f"\n[Qwen 3.5 Agent] Initiating request from {current_host} to Office M3 Max...")

    while True:
        try:
            start_time = time.time()
            response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            
            elapsed = time.time() - start_time
            content = response.json()['choices'][0]['message']['content']
            
            print(f"[Qwen 3.5 Agent] Success. Time elapsed: {elapsed:.2f}s")
            return content

        except requests.exceptions.Timeout:
            print(f"\n[ERROR] Request to Qwen 3.5 timed out after {TIMEOUT}s.")
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Could not connect to {API_URL}. Is the Cloudflare tunnel/Office Mac active?")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")

        # Interactive Recovery Protocol
        print("-" * 40)
        print("Choices: (r)etry, (w)ait 30s & retry, (b)ridge to OfficeMac, (s)kip/exit")
        choice = input("Option: ").lower().strip()
        
        if choice == 'r':
            print("Retrying now...")
            continue
        elif choice == 'w':
            print("Waiting 30 seconds...")
            time.sleep(30)
            continue
        elif choice == 'b':
            print(f"Relaying prompt to OfficeMac via GitHub Bridge...")
            bridge_cmd = f'python D:/hnxj-gemini/scripts/send_task.py "OfficeMac" "{prompt.replace('"', '\\"')}"'
            subprocess.run(bridge_cmd, shell=True)
            return "[RELAYED] Prompt sent to OfficeMac via Bridge. Check COMMAND_BUS.json for results."
        elif choice == 's' or not choice:
            return "[SKIPPED] Sub-agent call bypassed by user."
        else:
            print("Invalid choice. Defaulting to retry...")

def manage_model(action, model_name=None):
    """Sends model management commands to the Office Mac via Bridge."""
    if action == "list":
        cmd = "lms ls"
    elif action == "load" and model_name:
        cmd = f"lms load {model_name} --gpu=max"
    elif action == "unload":
        cmd = "lms unload --all"
    else:
        return "Invalid model command."
    
    print(f"Relaying '{action}' command to OfficeMac via GitHub Bridge...")
    bridge_cmd = f'python D:/hnxj-gemini/scripts/send_task.py "OfficeMac" "{cmd}"'
    subprocess.run(bridge_cmd, shell=True)
    return f"[MODEL TASKED] '{action}' command sent. Check COMMAND_BUS.json for output."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        # Check for model management keywords
        if args[0] in ["load", "unload", "list"]:
            res = manage_model(args[0], args[1] if len(args) > 1 else None)
            print(res)
            sys.exit(0)
            
        user_prompt = " ".join(args)
        print("\n" + "="*50)
        print(result)
        print("="*50 + "\n")
    else:
        print("Usage: python qwen_subagent.py 'your prompt here'")
