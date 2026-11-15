# quirkwright

![quirkwright banner](.github/images/banner.jpg)

Rules and checks for AI coding agents running on a Windows host. Agents are mostly trained on Linux transcripts, so they trip over what Git Bash, the PowerShell tool, the file tools and Windows processes actually do: a backslash lost in a heredoc, a file quietly saved with CRLF, `$!` that is not the Windows pid, a wait loop that never sees the job fail.

quirkwright is one skill plus a small standard-library script, `qw.py`. Each rule in it failed for a bare model on a clean run before it went in; rules the model already follows are folded into one line so they cost almost nothing.

## What you get

- **The skill** ([SKILL.md](skills/quirkwright/SKILL.md)): four short rules, with references loaded only when a rule applies (escapes, line endings and encoding, processes, waits, paths, plugins).
- **`qw.py`** (Python 3.9+, no dependencies, one JSON object out):
  - `check <files> [--expect-eol lf]`: CR bytes, control bytes, BOM, half-decoded escapes in what was just written.
  - `pid "<command>"`: real Windows pids for a command line, with start times, wait loops set aside.
  - `wait <log> --done RE --fail RE --deadline S`: waits on a log and stops on failure or deadline, never forever.
  - `doctor [--plugin NAME]`: live shells, the `python3` Store stub, path case, path headroom, stdout encoding, a plugin's installed version.
- **Hooks** ([hooks/](hooks/README.md)), shipped **off**: refuse a kill by image name, warn on backslashes in a Python heredoc, byte-check every Write and Edit.

## Install

Claude Code:

```
claude plugin marketplace add m4bwav/quirkwright
claude plugin install quirkwright@quirkwright
```

Or copy `skills/quirkwright/` into your agent's skills folder. The skill text is plain markdown, so Copilot, Codex and Cursor can read it too.

## Private notes

Facts about your own machine (hosts, ports, drive layout) go in `notes.md` inside `QUIRKWRIGHT_HOME` (default `~/.quirkwright`). The skill reads it at Step 0. Put a `leak-terms.txt` there too, and `tests/test_leak.py` fails if any of those terms ends up in a tracked file.

## Tests

```
python -m unittest discover -s tests
```

The eval suite (cases with a no-skill baseline) is in [skills/quirkwright/evals/evals.json](skills/quirkwright/evals/evals.json); how it runs is in [TESTS.md](skills/quirkwright/TESTS.md).

## Keeping current

Quirks change with every harness release, so the skill is an evergreen unit: its claims carry check dates and repros, and it is re-researched every couple of weeks. See [MAINTENANCE.md](skills/quirkwright/MAINTENANCE.md).

## License

MIT. See [LICENSE](LICENSE).
