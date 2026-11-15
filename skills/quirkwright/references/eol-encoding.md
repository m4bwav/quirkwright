# Line endings and encoding

Checked: Claude Code 2.1.x, Git Bash and PowerShell 7, Python 3.14, Windows 11, 2026-11-15.

| Quirk | Rule | Repro |
|---|---|---|
| Python text mode writes CRLF on Windows: an LF file rewritten with `open(p, 'w')` becomes a whole-file diff. | Read and write bytes (`rb`/`wb`), detect the file's newline, keep it. Or pass `newline=''` and write what you read. | `open('t','w').write('a' + chr(10))`, count byte 13: 1 |
| The Write tool has produced CRLF on one host and LF on another. | After a batch of writes run `qw.py check --expect-eol lf <files>` where the repo is LF. | `qw.py check <file>` shows `eol` |
| `npm install` rewrites lockfiles with CRLF. (unverified here) | Check `git diff --stat` for whole-file diffs; normalise byte-wise. | `npm install` in an LF repo |
| Python stdout to a console, pipe or redirect is cp1252: non-Latin text raises UnicodeEncodeError. Piped stdin decodes as cp1252 too. | `sys.stdout.reconfigure(encoding="utf-8")` (stdin, stderr too) in every script; `PYTHONIOENCODING=utf-8` for one-off runs; name `encoding="utf-8"` on every `open`. | `python -c "print(chr(0x5eb7))" > x.txt` exits 1 |

A plain `str.replace` on text read in text mode works on CRLF files (newlines are translated); it misses only on text decoded from `rb` bytes. `assert old in s` before replacing either way. Git's "LF will be replaced by CRLF" warning under `text=auto` is harmless.
