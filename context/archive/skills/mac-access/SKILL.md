---
name: mac-access
---
# mac-access

## Purpose
macOS remote node administration: SSH access, Full Disk Access for sshd/zsh, persistent MLX inference servers, sleep prevention.

## Setup Commands
```bash
sudo systemsetup -setremotelogin on          # Enable SSH
sudo pmset -a disablesleep 1                  # Prevent sleep
tmux new -s mlx_server                        # Persistent session
python -m mlx_lm.server --model mlx-community/Qwen2.5-32B-Instruct-8bit --port 8080
```

## Input
| Name | Type | Description |
|------|------|-------------|
| host_ip | str | e.g. `10.32.133.50` |
| model_id | str | HuggingFace MLX path |
| port | int | API port (default: 8080) |

## Output
| Name | Type | Description |
|------|------|-------------|
| ssh_tunnel | str | Verified key-based connection |
| api_endpoint | str | `http://{host}:{port}/v1/models` |

## Files
- [mlx_proxy.py](file:///D:/drive/omission/src/remote/mlx_proxy.py) — Python client
