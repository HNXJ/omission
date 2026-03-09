# Secure Remote Messaging & Task Execution

This system allows the **Main Agent** (Gemini CLI) to dispatch heavy tasks to the **Office Mac** (M3 Max) and the **Windows PC** from any network using your private GitHub repository as a secure message bus.

## 🚀 How it Works
1.  **COMMAND_BUS.json**: A private JSON file in `hnxj-gemini` acts as the queue.
2.  **Dispatcher**: The Main Agent writes a task to this file (Command, Target, ID).
3.  **Bridge Script**: Both local PCs run `scripts/remote_bridge.py`. They pull the repo every 30s, check for tasks assigned to them, execute the command, and push the results back.

## 🛠 Setup Instructions
To enable this on the Office Mac or Windows PC:
1.  Navigate to the `hnxj-gemini` directory.
2.  Run the bridge in the background:
    ```bash
    python3 scripts/remote_bridge.py &
    ```

## 📋 Command Format
Tasks are structured as follows:
```json
{
    "id": "task_001",
    "target": "OfficeMac",
    "command": "python3 /path/to/heavy_analysis.py",
    "status": "pending"
}
```

## 🪵 Status Flow
`pending` -> `running` -> `completed` | `failed`

## 🔐 Security
- No open ports required.
- Communication is encrypted via GitHub (HTTPS/SSH).
- Access is limited to authenticated Git users.
