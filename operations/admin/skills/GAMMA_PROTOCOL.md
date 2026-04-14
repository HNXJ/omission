# GAMMA: Explicit Markdown Transfer Protocol (The "Handoff")

This protocol defines the explicit staging-and-transfer mechanism for sharing logic, skills, and protocols between Sibling Nodes (e.g., Antigravity and Gemini CLI).

## 🧩 Core Philosophy
- **Isolated Contexts**: Agents maintain distinct active skill directories. They do NOT share a live file system.
- **Explicit Payloads**: Knowledge is strictly transferred via explicit, human-approved payload deliveries.
- **Human-in-the-Loop**: Approval is mandatory before any logic propagates across the cluster.

---

## 🏗️ Operational Workflow

### 1. Drafting & Internal Validation
An agent generates or modifies a markdown protocol locally within its own context.
- **File Location**: `skills/[SkillName].md` (Internal only).

### 2. Staging for Export
When a skill is deemed valuable for the Sibling Node, the agent generates a "Transfer Payload".
- **Target Directory**: `D:\drive\omission\Export_Staging\`
- **Naming Convention**: `PENDING_[TargetAgent]_[SkillName].md`
- **Target Agent**: `gemini_cli` or `antigravity`.

### 3. Notification & Review
The agent presents a summary and a diff of the staged file to the user.
- **Message**: "I have staged a new `[SkillName]` payload for `[TargetAgent]`. Awaiting review for transfer execution."

### 4. Transfer Execution (Triggered by USER)
Upon human approval, the agent executes the transfer.
- **Command**: `mv D:\drive\omission\Export_Staging\PENDING_... D:\drive\omission\skills\...` (or equivalent).
- **Security Check**: This command is ONLY run after explicit user approval.

### 5. Receipt Acknowledgment
The receiving agent parses the incoming markdown on its next execution loop.
- **Log**: `[Ingested new skill transferred from Sibling: SkillName]`.

---

## 💎 Best Practices
- **Never symlink**: Active skill directories must be physical copies.
- **Metadata**: Every payload should include a `Transferred-From` and `Timestamp` header.
- **Atomic Transfers**: Move the entire file; avoid appending to existing files during transfer.

---
*Status: Canonical Protocol Active as of 2026-04-14.*
