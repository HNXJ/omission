# Cross-Agent Communication Protocol (GAMMA)

This directory (`Export_Staging/`) serves as the designated, asynchronous communication and task-queuing hub for multiple AI agents (e.g., `omission-core`, `antigravity`) operating within the Omission workspace. 

## 1. Naming Convention
All payloads, plans, and task requests MUST strictly follow this naming format:
`PENDING_[TargetAgent]_[Task_Description].md`

**Examples:**
- `PENDING_antigravity_optimize_nwb_queries.md`
- `PENDING_omission_core_execute_laminar_psd.md`

## 2. Workflow & Approval Process
1. **Drafting**: An agent writes a detailed plan or request into this directory using the `PENDING_` prefix.
2. **Human Approval**: By default, physical execution or transfer of large tasks queued here requires explicit human approval. The human user acts as the final arbiter and router.
3. **Execution**: Once approved, the target agent reads the payload and executes the plan.
4. **Resolution**: Upon completion or failure, the executing agent MUST move the payload into the daily archive folder located at `Export_Staging/archive/YYYYMMDD/` (e.g., `20260421/`), rename it to `RESOLVED_[TargetAgent]_[Task_Description].md`, and append a brief execution summary at the top of the file.

## 3. Payload Structure
Every queued plan MUST contain:
- **Target**: The specific agent expected to read it.
- **Context**: A brief state summary of the repository relevant to the task.
- **Objectives**: Clear, atomic, and scope-preserving engineering or analytical tasks.
- **Constraints**: Any specific technical rules or boundaries to observe.
