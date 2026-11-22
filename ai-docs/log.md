# Log: quirkwright

- 2026-11-15: steps A-D (harvest, prior art, design, baseline) written under ai-docs/.
- 2026-11-15: step E built the plugin 0.1.0: SKILL.md hub + 6 references, qw.py (check, pid, wait, doctor), hooks off (hooks.example.json), tests (hw, hooks, leak; 22 pass), sidecar in the vault, private GitHub repo. evals moved to skills/quirkwright/evals/ with temp paths scrubbed to <TMP>.
- 2026-11-15 step F prove: clean baseline 3/20 fail (session-1 14/17 not reproduced), with skill 25/26, rules 2-4,6,8 folded into one basics line, worth TRIM; qw.py pid misses quoted Git Bash exe paths.
- 2026-11-15 step G: working notes (design, harvest, prior art, baseline, prove) moved to the private sidecar's ai-docs/; leak test now checks ai-docs/ too. qw.py pid matches Git Bash's quoted exe command lines (test added, 23 pass). esc-write-backslash-u eval now checks behaviour, not a literal. History still holds the old notes: squash before the repo goes public.
- 2026-11-15 step H: renamed hostwright to quirkwright (repo, skill, qw.py, QUIRKWRIGHT_HOME): 'hostwright' is an active product's GitHub org and site; quirkwright had no repos or user on GitHub.
- 2026-11-15: 0.2.0 released (public, fresh repo m4bwav/quirkwright), installed. Wiki waits on the first page.
- 2026-11-15: 0.2.1 released (kill guard + byte check hooks on, heredoc off), installed. Wiki pages written and verified, not pushed: no wiki repo yet (first page not saved). SKILL.md hooks line fixed (said shipped off).
- 2026-11-21: 0.2.2 rule 5 "Picking up skill and plugin changes" (/reload-skills, user-typed /reload-plugins, new session only for hooks/MCP/settings/CLAUDE.md; no app restart), L-014, C-004. Not tagged.
- 2026-11-21: Remote Control: /reload-plugins prints "/reload-plugins isn't available over a remote connection in this session."; /reload-skills works remotely. Rule 5 says remote plugin changes need a fresh session (L-015).
- 2026-11-21: reload rule marked volatile: observed on Claude Code 2.1.281, two verify-at-use claims (recheck 30 days) in evergreen.json, rule 5 says re-test before asserting (C-005).
