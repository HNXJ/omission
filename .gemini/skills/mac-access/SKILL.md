---
name: mac-access
description: A comprehensive guide for configuring full terminal access, SSH, and MLX servers on macOS.
version: 1.0.0
---

# SKILL: Mac Full Terminal Access & Remote Server Guide

This skill provides a definitive guide for setting up and maintaining full terminal access on macOS, specifically optimized for remote neuro-analysis and MLX inference servers.

## 1. Remote Login (SSH)
To allow remote access from other machines:
1.  **System Settings** > **General** > **Sharing**.
2.  Toggle **Remote Login** to **ON**.
3.  Click the (i) icon to verify that your user is permitted.
4.  **Terminal Command**: `sudo systemsetup -setremotelogin on`

## 2. Full Disk Access (FDA)
Required for the terminal and SSH to access data in protected folders (e.g., `Documents`, `Desktop`, `Downloads`):
1.  **System Settings** > **Privacy & Security** > **Full Disk Access**.
2.  Click the `+` button and add:
    -   `/bin/zsh` (or your preferred shell)
    -   `/usr/bin/sshd` (to allow remote file access)
    -   **Terminal.app** (or iTerm2)

## 3. Persistent Sessions & Power
To ensure the server doesn't die when you disconnect or the Mac sleeps:
1.  **Prevent Sleep**:
    -   **System Settings** > **Displays** > **Advanced** > "Prevent automatic sleeping on power adapter when the display is off".
    -   **Terminal Command**: `sudo pmset -a disablesleep 1`
2.  **Persistent Shell**: Use `tmux` or `screen` to keep long-running processes (like MLX servers) alive.
    -   Start session: `tmux new -s server`
    -   Detach: `Ctrl+B`, then `D`
    -   Re-attach: `tmux attach -t server`

## 4. MLX Server Setup
For high-performance inference:
1.  **Install**: `pip install mlx-lm`
2.  **Launch**: `python -m mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-8bit --port 8080`
3.  **Local Access**: Access from your Windows machine at `http://10.32.133.50:8080/v1`

## 5. Security & Maintenance
- **Static IP**: Ensure your Mac has a reserved IP in the router/network settings (`10.32.133.50`).
- **Keys**: For password-less login, use `ssh-copy-id nejath@10.32.133.50`.
- **Updates**: Regularly run `softwareupdate -l` to check for security patches.
