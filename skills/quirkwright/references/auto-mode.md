# Auto mode blocks

Checked: Claude Code 2.1.x, auto permission mode, 2026-11-22. Source: about 200 classifier denials in one owner's transcripts (counts in the private sidecar).

Auto mode sends every tool call that no allow rule covers to a classifier. A denial comes back as a tool error: `Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Category]`.

## What the agent does when blocked

| Situation | Rule |
|---|---|
| `no verdict (error)` or `shell moved since leading cd` | Not a denial. Retry once, as is or from an absolute path. |
| A real denial | It covers the **outcome**, not the command. Do not retry in pieces, through another tool, in a script, through a subagent or in a later session. Finish the rest of the task, then tell the user what was blocked, the category, and the one-line allow rule that would cover it. |
| The user asks you to loosen auto mode | You cannot, even with their consent. Edits to `settings.json`, to a file that holds the rules, or a script that writes them are all `[Undermining Oversight]`. The user switches to manual mode and approves, or runs `qw.py automode` themselves. |
| A task needs a blocked action now | Ask the user to switch the permission mode to ask/default (Shift+Tab in the terminal; the mode picker by the prompt box on the phone and in the desktop app), approve the prompt, then switch back. |

## Categories seen, and the preset that covers each

| Category | Typical blocked call | `qw.py automode` preset |
|---|---|---|
| Merge Without Review, Destructive or Unwanted Actions | `gh pr merge N --squash --delete-branch` on the owner's repo | `own-repo-gh` |
| Create Public Surface | `gh repo create OWNER/x --public`, visibility to public | `own-repo-public` |
| Public Data-Sharing Upload | Workshop or asset uploads of the owner's items | `own-uploads` |
| Code from External | `pip install git+https://...`, `uv sync`, `git clone` into a custom-nodes folder | `installs` |
| Unauthorized Access, Bot Check Circumvention | `curl` of public pages, `yt-dlp`, model downloads | `network-reads` |
| Interfere With Workloads | `Stop-Process -Id N`, a queue clear on the owner's GPU server | `local-workloads` |
| Undermining Oversight, Instruction Poisoning, Create Unsafe Agents | nested `claude -p`, HANDOFF and ledger writes, test runner scripts | `agent-tooling` |
| Git Destructive, Irreversible Local Destruction, Shared Scratch Sweep | `git reset --hard` in an agent worktree, `rm -rf` of a temp eval folder | `scratch-cleanup` |
| (environment changes) | `setx NAME value` for the owner's own tools | `user-env` |
| External System Writes | writes to someone else's repo | `others-repos` (opt-in) |
| (registry publishing) | `npm publish`, `npx jsr publish` | `publish` (opt-in) |

Opt-in presets are never part of `all`: name them, and only once the owner has said so for that case.

## qw.py automode (the owner runs it)

```
QW automode list                       # presets, the values they need, the rules already in settings
QW automode plan all                   # what apply would add; writes nothing
QW automode apply all --apply          # backs up settings.json, adds the rules (each tagged [qw:<preset>])
QW automode apply --rule "TEXT" --apply  # one extra prose rule
QW automode revert --apply             # removes every [qw:...] rule again
```

Values such as the GitHub owner, the LAN hosts and the folders come from `QUIRKWRIGHT_HOME/automode.json` (`{"owner": "...", "hosts": ["..."], "folders": ["..."], "people": "..."}`) or `--set key=value`. A preset whose values are missing is skipped and named in `missing`.

Settings are read when a session starts: new sessions get the rules. An agent that runs `apply` in auto mode is blocked, which is how it should be. The owner runs it in their own shell, in another tool, or approves it in manual mode.

Prose allow rules work best when they name the owner, the scope (their repos, their machines, agent-made folders) and the date they were authorized. A rule that says "allow everything" is ignored or overridden by the defaults.
