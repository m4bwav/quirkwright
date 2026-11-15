# Escapes and backslashes

Checked: Claude Code 2.1.x, Bash tool = Git Bash, Write/Edit tools, Windows 11, 2026-11-15. Run the repro before relying on a quirk you have not seen this session.

| Quirk | Rule | Repro |
|---|---|---|
| A quoted heredoc (`<<'EOF'`) in the Bash tool still loses one level: a doubled backslash arrives single. | Never carry backslashes through a heredoc. Write the file with the Write tool, or build the character in code: `chr(92)` (Python), `String.fromCharCode(92)` (node). | `cat <<'EOF'` with body `a`, two backslashes, `b`: prints one backslash |
| Windows paths in a plain Python string turn `\v \f \a \b` and octal runs into control bytes, silently. | Forward slashes in paths (Windows accepts them), or raw strings written with the Write tool. Regex always raw. Then `qw.py check`. | `python -c "print(repr('D:\video'))"` shows `\x0b` |
| Code that writes code: an escaped newline in a heredoc becomes a real newline inside the generated literal (SyntaxError). | Write generators with the Write tool; use `chr(10)` in the generated source. | generate a .py from a heredoc with an escaped newline in a string, run it |
| The Write and Edit tools decode a backslash-u escape into the character (`u003c` lands as `<`); Edit then refuses as a no-op. | Build the escape in code (`chr(92) + "u003c"`); `qw.py check` flags half-decoded `u00XX`. | Write a file holding the escape, `grep -c u003c` gives 0 |
| The Write tool strips trailing spaces, even inside string literals. | Build trailing whitespace in code (`chr(32)`). | Write a line ending in two spaces, `grep -c ' $'` |
| Git Bash (MSYS) rewrites an argument starting with `/` into a Windows path (`/rerun` became `C:/Program Files/Git/rerun`; `tasklist /FI` too). | Prefix `MSYS_NO_PATHCONV=1`, double the slash (`//FI`), or run it from the PowerShell tool. | `python -c "import sys;print(sys.argv)" /foo` |

Unverified (no repro): a heredoc body with an apostrophe sometimes fails with "unexpected EOF"; use the Write tool instead of retrying. The PowerShell tool's safety check can read a regex as a path being deleted; put deletes in their own call.
