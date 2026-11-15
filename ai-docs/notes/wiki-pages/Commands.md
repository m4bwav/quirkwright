`qw.py` lives in `skills/quirkwright/scripts/`. Every command prints one JSON object and exits 0 when `ok` is true, 1 otherwise. The outputs below are from 0.2.1 on Windows 11, Python 3.14, run in a scratch folder.

## check

```sh
python qw.py check FILES... [--expect-eol lf|crlf]
```

Reports, per file: CR and LF counts, the line-ending style, control bytes (line and byte value), a UTF-8 BOM, lines with trailing spaces, and lines where a `\u` escape was decoded. `issues` lists what makes `ok` false.

A file saved with CRLF, checked with `--expect-eol lf`:

```sh
python qw.py check crlf.py --expect-eol lf
```

```text
{
  "ok": false,
  "files": {
    "crlf.py": {
      "cr": 2,
      "lf": 2,
      "eol": "crlf",
      "controls": [],
      "bom": false,
      "trailing_space_lines": [],
      "lost_backslash_u_lines": [],
      "issues": [
        "eol-not-lf"
      ]
    }
  }
}
```

Without `--expect-eol`, CRLF alone is not an issue. A BOM always is:

```sh
python qw.py check bom.md
```

```text
{
  "ok": false,
  "files": {
    "bom.md": {
      "cr": 0,
      "lf": 1,
      "eol": "lf",
      "controls": [],
      "bom": true,
      "trailing_space_lines": [],
      "lost_backslash_u_lines": [],
      "issues": [
        "bom"
      ]
    }
  }
}
```

A Python line meant as `'C:` + backslash + `folder` + backslash + `bin'`, where the backslashes were lost and `\f` and `\b` became form feed (12) and backspace (8):

```sh
python qw.py check esc.py
```

```text
{
  "ok": false,
  "files": {
    "esc.py": {
      "cr": 0,
      "lf": 1,
      "eol": "lf",
      "controls": [
        {
          "line": 1,
          "byte": 12
        },
        {
          "line": 1,
          "byte": 8
        }
      ],
      "bom": false,
      "trailing_space_lines": [],
      "lost_backslash_u_lines": [],
      "issues": [
        "control-bytes"
      ]
    }
  }
}
```

## pid

```sh
python qw.py pid "FULL COMMAND LINE" [--all]
```

Lists the Windows processes whose command line matches, with pid and start time, so you can kill the one you started and check it is the right one. Use it in place of `$!`, which in Git Bash is the MSYS pid. Wait loops and monitors whose own command line contains the pattern are set aside in `skipped`; `--all` includes them. Git Bash's quoted exe command lines (`"...sleep.exe" 60`) match a plain `sleep 60`.

With no match:

```sh
python qw.py pid "no-such-command-xyz 123"
```

```text
{
  "ok": false,
  "pattern": "no-such-command-xyz 123",
  "matches": [],
  "skipped": [],
  "note": "kill only these pids, after checking start time; never by image name"
}
```

## wait

```sh
python qw.py wait LOG --done REGEX --fail REGEX --deadline SECONDS [--interval S] [--new-only]
```

Polls a log until a line matches `--done`, a new line matches `--fail`, or the deadline passes. It never waits forever.

- `--fail` counts only lines added after the wait started. A failure already in the log when you start does not stop the wait (shown below).
- `--done` counts lines already in the log too, unless `--new-only` is given.

The job already finished:

```sh
python qw.py wait job.log --done DONE --fail "Traceback|ERROR" --deadline 5
```

```text
{
  "ok": true,
  "result": "done",
  "waited_s": 0.0
}
```

A failure line written to the log while waiting:

```sh
python qw.py wait run.log --done DONE --fail "Traceback|ERROR" --deadline 10 --interval 1
```

```text
{
  "ok": false,
  "result": "failed",
  "new_fail_lines": 1,
  "waited_s": 2.0
}
```

A log that already held `Traceback` when the wait started, and nothing new:

```sh
python qw.py wait bad.log --done DONE --fail "Traceback|ERROR" --deadline 2 --interval 1
```

```text
{
  "ok": false,
  "result": "deadline",
  "waited_s": 2.0,
  "hint": "check the job is alive (qw.py pid) before waiting again"
}
```

## doctor

```sh
python qw.py doctor [--plugin NAME]
```

Read-only. Reports `platform`, `python`, `stdout_encoding`, which of `bash`, `pwsh`, `powershell` and `py` are on PATH, whether this is an MSYS shell, whether `python3` is the Store stub, the cwd and its length, `path_headroom` (259 minus the cwd length), whether `~/.claude.json` has an MCP project key that differs from the cwd only by case, and with `--plugin` the plugin's `installPath` and version from `installed_plugins.json`. Warnings are added when `python3` is the stub, headroom is under 110, the MCP key case differs, or stdout is not UTF-8.
