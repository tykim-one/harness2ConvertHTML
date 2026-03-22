# Team Runtime Diagnosis

## Refined conclusion
Two distinct failure modes were confirmed.

### Failure mode 1 — detached CLI tmux workaround
- When `$team` CLI was launched from a detached tmux session because the current shell was not already inside tmux, startup succeeded but the topology was unstable and team state disappeared soon after.
- This path was not reliable enough for agent-driven completion evidence.

### Failure mode 2 — prompt-mode codex workers die immediately
- Re-running with `OMX_TEAM_WORKER_LAUNCH_MODE=prompt` avoided the tmux-leader requirement and kept team state long enough to inspect.
- In this mode the team did **not** vanish immediately; instead it failed cleanly with all workers dead and all tasks still pending.
- Concrete evidence:
  - `omx team status implement-the-first-true-hwp-d` showed `phase=failed`, `workers: total=3 dead=3`, `tasks: pending=21 in_progress=0`.
  - `.omx/state/team/implement-the-first-true-hwp-d/monitor-snapshot.json` recorded all workers dead with zero turn counts.
  - `.omx/state/team/implement-the-first-true-hwp-d/config.json` recorded prompt-mode worker PIDs.
  - local `kill -0` checks showed those PIDs were already dead.

## Most likely root cause
The prompt-mode runtime spawns Codex workers **without a TTY**:
- `spawnPromptWorker(...)` uses `spawn(..., { stdio: ['pipe', 'ignore', 'ignore'] })`
- file: `/Users/tykim/.local/lib/node_modules/oh-my-codex/dist/team/runtime.js`

This strongly suggests the `codex` CLI exits immediately in prompt-mode because it is being started in a non-interactive, non-TTY process environment.

## Supporting code evidence
- Default launch mode is `interactive` unless `OMX_TEAM_WORKER_LAUNCH_MODE=prompt` is set:
  - `tmux-session.js:335-340`
- Interactive mode requires an existing tmux leader pane (`TMUX` must be set):
  - `runtime.js:startTeam(...)`
- Prompt-mode worker spawning uses non-TTY stdio:
  - `runtime.js:spawnPromptWorker(...)`
- When all workers are dead while work remains, monitor marks the team failed:
  - `runtime.js:monitorTeam(...)`

## Confidence
- **High** that prompt-mode Codex workers are dying immediately because they are launched without a TTY.
- **Medium-high** that the earlier detached CLI workaround was a separate topology problem, but the deeper blocker for agent-driven use here is the lack of a stable supported worker runtime outside a real live tmux leader pane.

## Safest next action
### Best operational path
Run `$team` from a **real user-owned live tmux leader pane**.

### Best engineering fix
Update OMX prompt-mode worker launching so Codex workers get a PTY (or use a supported headless worker path if one exists).

### Practical implication for this session
From this agent context, `$team` is currently **not a reliable execution surface** for real implementation progress unless the runtime itself is changed or a live tmux leader pane is used.
