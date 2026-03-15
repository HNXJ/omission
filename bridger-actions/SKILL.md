---
name: bridger-actions
description: Provides tools for safe peer-to-peer messaging using Git-relays and SSH/RSA encryption. Use for transferring code, results, or messages between secure compute engines.
---

# Bridger Actions Skill

This skill enables secure communication between compute engines using the **Bridger** module.

## Core Concepts
- **Git-Relay**: A private Git repository acts as the central mailbox.
- **End-to-End Encryption**: RSA keys are used to encrypt payloads locally before they are pushed to the cloud.
- **Bridger Address**: Your public RSA key string.

## Common Workflows

### 1. Initialize & Get Address
Run the bridger setup to get your unique address to share with your partner.
```bash
python /Users/hamednejat/workspace/Computational/bridger/bridger.py --address
```

### 2. Sending a Message
```python
from bridger import BridgerMod
bridger = BridgerMod(relay_url="...", partner_pubkey_path="partner.pub")
bridger.send(mode="text", msg="Optimization complete.", partner_id_hash="...")
```

### 3. Checking & Reading Mail
```python
bridger.check() # Pulls new messages
msg = bridger.read() # Decrypts and returns the most recent message
print(msg['data'])
```

## Safety Hardwires
- **Restricted Keys**: Bridger RSA keys are stored in `~/.ssh/bridger_keys` with 600 permissions.
- **No Plaintext**: Message contents never touch the Git relay in unencrypted form.
