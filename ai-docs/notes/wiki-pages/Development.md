## Layout

| Path | Holds |
|---|---|
| `.claude-plugin/plugin.json`, `marketplace.json` | Plugin manifest and the one-plugin marketplace |
| `skills/quirkwright/SKILL.md` | The skill: Step 0 and the four rules |
| `skills/quirkwright/references/` | escapes, eol and encoding, processes, waits, paths, plugins and the panel |
| `skills/quirkwright/scripts/qw.py` | check, pid, wait, doctor |
| `skills/quirkwright/evals/evals.json`, `TESTS.md` | Eval cases with a no-skill baseline |
| `hooks/` | `guards.py`, `hooks.json` (on), `hooks.example.json` (off) |
| `tests/` | Unit tests, including the hooks and the leak test |

## Tests

```sh
python -m unittest discover -s tests
```

23 tests pass at 0.2.1. There is no CI workflow; tests run locally before each merge. Set `QUIRKWRIGHT_HOME` to the folder with your `leak-terms.txt` so the leak test checks every tracked file against your private terms.

## Rules for changes

- Never put owner paths, hosts, ports or names in a tracked file; they go in `QUIRKWRIGHT_HOME/notes.md`.
- Python edits keep line endings: edit in binary mode.
- Write Python that holds backslashes with a file tool, not a Bash heredoc.
- Each change gets a CHANGELOG entry with its reason, and the version in `plugin.json`.

## Keeping current

The skill is an evergreen unit on a 14-day research cycle. Its claims in `evergreen.json` carry check dates and repros; a repro that stops failing is a learning and a refresh trigger.
