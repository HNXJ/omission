---
name: mac-access
description: Administrative protocol for managing remote SSH access, Full Disk Access (FDA), and MLX inference servers on macOS.
---
# skill: mac-access

## When to Use
Use this skill when configuring the macOS analytical node for remote collaboration. It is essential for:
- Enabling SSH access (`Remote Login`) for other agents or human users.
- Granting `Full Disk Access` to `/usr/bin/sshd` and `/bin/zsh` to bypass Sandbox restrictions.
- Starting and maintaining persistent MLX servers (e.g., Qwen2.5-32B) for high-speed local inference.
- Preventing system sleep during long-running background simulations.

## What is Input
- **Host Info**: IP Address (e.g., `10.32.133.50`) and Username.
- **Privacy Settings**: GUI pathing for macOS Security & Privacy panels.
- **MLX Model ID**: HuggingFace path (e.g., `mlx-community/Qwen2.5-32B-Instruct-8bit`).

## What is Output
- **Stable Connection**: Verified SSH tunnel with password-less (Key-based) entry.
- **Live Endpoint**: OpenAI-compatible local API (default: port `8080`).
- **Persistent Process**: Background `tmux` sessions that survive terminal disconnects.

## Algorithm / Methodology
1. **Sharing Activation**: `sudo systemsetup -setremotelogin on` to enable core SSH services.
2. **FDA Authorization**: Manual addition of shells and daemons to the "Full Disk Access" list in Privacy settings.
3. **Power Persistence**: `sudo pmset -a disablesleep 1` to ensure analytical continuity.
4. **Session Management**: Uses `tmux` to encapsulate MLX server instances, allowing detachment/reattachment.
5. **Security Hardening**: Recommends `ssh-copy-id` for key-based auth and reserved Static IPs.

## Placeholder Example
```bash
# 1. Start Persistent MLX Inference Server
tmux new -s mlx_server
python -m mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-8bit --port 8080

# 2. Access from Remote Node
# curl http://10.32.133.50:8080/v1/models
```

## Relevant Context / Files
- [jax-actions](file:///D:/drive/omission/.gemini/skills/jax-actions/skill.md) — For cross-node GPU/TPU coordination.
- [src/remote/mlx_proxy.py](file:///D:/drive/omission/src/remote/mlx_proxy.py) — The Python client for the MLX server.
