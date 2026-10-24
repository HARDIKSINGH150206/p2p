# AGENTS.md — Git Collaboration Rules (Two-Person Team)

**Purpose:** Mandatory, strict, actionable Git workflow for our two-person team.
We work on separate feature branches and merge into `main` only through
reviewed pull requests. These rules are the single source of truth for every
coding task involving Git operations.

---

## Mandatory Git Workflow

### 1. Before starting work
- Inspect the repository instructions, working tree, current branch, and remotes.
- `git status`, `git branch`, `git remote -v`.
- Fetch the latest remote updates: `git fetch <remote>`.
- Safely synchronize the current feature branch when necessary (rebase or merge
  only the specific upstream changes that are required, not a blind pull of `main`).

### 2. During development
- Make all task-related changes **only** on the assigned feature branch.
- Preserve existing work, project architecture, file/folder structure, and
  commit history.
- Never commit unrelated files or changes; keep each commit focused on the
  assigned task.

### 3. Before every push
- `git fetch <remote>` to obtain the latest remote state.
- Inspect local and remote changes (`git status`, `git log --oneline <remote>/...`...).
- Safely integrate relevant upstream commits **if required** (e.g. rebase onto the
  latest `main` or merge a specific other branch). Never push blindly.

### 4. Conflict handling
- Resolve conflicts carefully without discarding local or teammates' work.
- If safe resolution is uncertain, **stop and ask for guidance** before proceeding.
- Preserve both sides when in doubt; mark the resolution clearly.

### 5. Commit and push
- Review changes (`git diff`, `git diff --cached`).
- Run relevant tests before committing.
- Commit **all** intended changes with a clear, descriptive message.
- Push to the correct feature branch only (`git push <remote> <branch>`).
- Ensure no intended changes remain uncommitted or unpushed.

### 6. Protect `main`
- **Never** push directly to `main`, force-push, rewrite shared history, or
  merge another feature branch without explicit authorization.
- Integrate changes through pull requests and team review only.

### 7. Verify results
- Confirm the push succeeded (`git status`, `git log`.
- Report the branch name, commit hash, tests performed, synchronization status,
  and any remaining issues.

### 8. Failure handling
- If authentication, permissions, divergence, or other problems prevent a safe
  operation, **stop and report the exact issue**.
- Never claim an operation succeeded without verification.

---

## Additional Rules

- **Inspect existing `AGENTS.md` files and project documentation** before making
  changes. Preserve compatible instructions and avoid duplicating or contradicting
  existing rules.
- **Do not blindly pull `main` or another feature branch** on every operation;
  integrate only the appropriate upstream changes.
- **Do not use destructive commands** such as `git reset --hard`, `git clean`, or
  force-push as routine recovery methods.
- **Never overwrite** the remote repository with a local snapshot. Git pushes
  commits, not a wholesale replacement of the repository.
- **Keep changes focused** on the assigned task and never silently include
  unrelated files or changes.
- **Treat these rules as mandatory** for every coding task involving Git operations.

---

## Workflow Summary (quick reference)

| Step | Action |
|------|--------|
| Before work | `git fetch`; inspect branch, remote, working tree |
| Development | Changes on feature branch only; preserve history |
| Before push | `git fetch`; inspect local vs remote; integrate if needed |
| Conflicts | Resolve carefully; stop & ask if uncertain |
| Commit/push | Review, test, commit all, push to feature branch only |
| Protect main | PRs only; no direct/force pushes |
| Verify | Report branch, hash, tests, sync status, issues |
| Failures | Stop & report exact issue; never falsely claim success |

---

*Adopted for our two-person team to prevent history rewrites, lost work, and
unintended `main` modifications. Treat these rules as mandatory for every Git
operation.*