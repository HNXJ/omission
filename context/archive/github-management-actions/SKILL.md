---
name: github-management-actions
description: Standardized workflows for managing GitHub repositories, including Pull Request (PR) evaluation and merging protocols. Use when reviewing incoming changes to ensure repository integrity.
---

# GitHub Management Actions Skill

This skill codifies the rules for reviewing and merging Pull Requests (PRs) or Merge Requests on this local machine.

## PR Evaluation Protocols

### 1. Automatic Acceptance
Review and merge PRs automatically ONLY if they consist of the following operations:
- **Add**: Introduction of new files.
- **Edit**: Modification of existing files without deletions.

### 2. Manual Review Required
DO NOT merge PRs automatically; instead, flag them for manual one-by-one verification if they contain:
- **Delete**: Removal of any existing files or directories.
- **Replace**: Complete replacement of files that involves significant deletions.

## Review Workflow
1. **List PRs**: Use `gh pr list` to see pending requests.
2. **Inspect Diff**: Use `gh pr diff <number>` or `gh pr view <number>` to check the operation types.
3. **Verify Compliance**:
   - If only "add" or "edit", proceed to merge.
   - If "delete" or "replace", report to user for manual check.
