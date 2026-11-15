## Install

In Claude Code (these two lines are from the README and were not run for this wiki):

```sh
claude plugin marketplace add m4bwav/quirkwright
claude plugin install quirkwright@quirkwright
```

Restart Claude Code after installing or updating, so the hooks load. Other agents (Copilot, Codex, Cursor) can read `skills/quirkwright/SKILL.md` as plain markdown and run `qw.py` directly; the hooks are Claude Code only.

## What needs what

| Part | Needs |
|---|---|
| `qw.py` | Python 3.9 or later, nothing else. Call it as `python`, not `python3`: on Windows `python3` is often the Microsoft Store stub. |
| `qw.py pid` | Windows (it reads process command lines through CIM) |
| The hooks | Claude Code, and the `py` launcher, since `hooks.json` runs `py -3` |

The examples on these pages ran on Windows 11 with Python 3.14. macOS and Linux were not tested.

## First commands

Run `doctor` once in a new environment. It prints one JSON object with the shells it found, whether `python3` is the Store stub, how much path length is left under the cwd, and whether stdout is UTF-8, plus a `warnings` list. Its output names local paths, so it is not shown here.

```sh
python qw.py doctor --plugin quirkwright
```

After writing a file, check it:

```sh
python qw.py check good.py --expect-eol lf
```

```text
{
  "ok": true,
  "files": {
    "good.py": {
      "cr": 0,
      "lf": 1,
      "eol": "lf",
      "controls": [],
      "bom": false,
      "trailing_space_lines": [],
      "lost_backslash_u_lines": [],
      "issues": []
    }
  }
}
```

The exit code is 0 when `ok` is true and 1 otherwise. More in [Commands](Commands).

## Private notes

Facts about your own machine (hosts, ports, drive layout) go in `notes.md` inside `QUIRKWRIGHT_HOME` (default `~/.quirkwright`). The skill reads it at its first step. A `leak-terms.txt` there makes the repository's leak test fail when any of those terms ends up in a tracked file (see [Development](Development)).
