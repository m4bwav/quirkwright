## Why did my `taskkill /IM` call get refused?

The kill guard hook is on since 0.2.1. A kill by image name ends every process with that name, including other sessions' jobs and local servers. Find the pid with `qw.py pid "<full command>"` and kill that pid. See [Hooks](Hooks).

## The byte check did not warn about CRLF. Is it broken?

No. The hook runs `qw.py check` without `--expect-eol`, and CRLF alone is not an issue then. Run `qw.py check FILE --expect-eol lf` when the file must be LF.

## My wait loop ran to the deadline although the log says Traceback.

`qw.py wait --fail` counts only failure lines added after the wait started. An old failure in the log is set aside, so a re-run of a job that writes to the same log is not stopped by the last run's error. See [Commands](Commands#wait).

## Does it work on macOS or Linux?

The rules and `check` and `wait` are plain Python and not tied to Windows, but they were only tested on Windows. `pid` reads Windows process command lines. The hooks run `py -3`, which is the Windows launcher.

## Why is the heredoc hook off?

The owner turned on only the kill guard and the byte check for 0.2.1. The heredoc warning is still built and tested; [Hooks](Hooks) says how to turn it on.

## Which version do I have?

`python qw.py doctor --plugin quirkwright` reads `installPath` from Claude Code's `installed_plugins.json`. The plugin cache keeps old versions next to the live one, so a glob of the cache folder can pick the wrong one.
