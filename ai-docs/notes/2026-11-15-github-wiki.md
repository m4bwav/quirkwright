# GitHub wiki for quirkwright 0.2.1

Status: pages written and checked, **not published**. `wikiwright preflight` returned `no-wiki-repo` (ls-remote of quirkwright.wiki.git: not found; /wiki redirects to the repo). Someone must save a first page at https://github.com/m4bwav/quirkwright/wiki/_new before a push can work.

## Pages

Home, Getting-Started, Rules, Commands, Hooks, FAQ, Versions-and-Upgrading, Development, _Sidebar, _Footer. Copies are in [wiki-pages/](wiki-pages/). Pages naming the version: Home (indirectly), Getting-Started, Commands, Hooks, FAQ, Versions-and-Upgrading, Development, _Footer.

## Publish (after the first page exists)

1. `git clone https://github.com/m4bwav/quirkwright.wiki.git` next to the repo clone.
2. Copy `ai-docs/notes/wiki-pages/*.md` in, commit ("Wiki for 0.2.1: <pages>"), `git push` (master, fast-forward over the placeholder).
3. `wikiwright.py live m4bwav/quirkwright <wiki dir>`.

## Verification

- Program: [2026-11-15-wiki-verify.py](2026-11-15-wiki-verify.py) `QW_PY WORK_DIR`; saved output [2026-11-15-wiki-verify.out.txt](2026-11-15-wiki-verify.out.txt). Run against the installed 0.2.1 `qw.py` and `hooks/guards.py` on Windows 11, Python 3.14.
- `wikiwright check --version 0.2.1`: 8 pages, 0 errors. `outputs`: 11 checked, 0 missing. everwrite tells: 0 strong.
- Repository tests: 23 pass.
- Not tested: install and update lines, `doctor` output (names local paths), `pid` with a live match, macOS and Linux.

## Facts the README lacks

1. `qw.py wait --fail` counts only failure lines added after the wait starts; an old failure in the log runs to the deadline.
2. `--done` counts existing lines unless `--new-only`.
3. `qw.py check` without `--expect-eol` does not flag CRLF, so the byte-check hook passes CRLF files silently.
4. The hooks run `py -3`: Windows `py` launcher required.
5. The kill guard blocks with exit 2; the check hook only adds context.

## Inaccuracies found in shipped docs

1. SKILL.md 0.2.1 still said the hooks ship off; fixed on main after the tag (ships with the next release).
