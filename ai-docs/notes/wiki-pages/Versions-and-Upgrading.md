| Version | Date | Changes |
|---|---|---|
| 0.2.1 | 2026-11-15 | `hooks/hooks.json` ships the kill guard and the byte check on. The heredoc warning stays off in `hooks.example.json`. |
| 0.2.0 | 2026-11-15 | First public release. `qw.py pid` matches Git Bash's quoted exe command lines. Leak test covers every tracked file. All hooks shipped off. |
| 0.1.0 | 2026-11-15 | Created (private): the skill, six references, `qw.py` with check, pid, wait and doctor, hooks off. |

## Upgrading from 0.2.0 to 0.2.1

```sh
claude plugin marketplace update quirkwright
claude plugin update quirkwright@quirkwright
```

Restart Claude Code so the hooks load. After that, a kill by image name is refused and Write and Edit results get a byte-check warning when something is wrong. Nothing else changed: `qw.py` and the skill text are the same as in 0.2.0, apart from the version and the hooks line.

The update lines were not run for this wiki under the `quirkwright` marketplace name; the owner's install updated through a local marketplace.

Full history: [CHANGELOG](https://github.com/m4bwav/quirkwright/blob/main/skills/quirkwright/CHANGELOG.md).
