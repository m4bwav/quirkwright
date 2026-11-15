# HANDOFF: quirkwright

Status: 0.1.0 built (step E); step F (prove) done 2026-11-15, see notes/prove.md: clean baseline 3/20 fail, with skill 25/26, worth TRIM (applied). Private repo, working name.

## State
- Step G done 2026-11-15: owner-specific notes live in the sidecar ($QUIRKWRIGHT_HOME/ai-docs/); leak test covers every tracked file. 23 unit tests pass.
- Evals: see the sidecar's ai-docs/notes/prove.md (clean baseline 3/20 fail; with skill 26/26 after fixes; worth TRIM applied).
- Hooks are written and tested but OFF (hooks/hooks.example.json). Waits on the owner's yes.

## Next
1. Wiki: waits on the owner saving the first wiki page; then run wikiwright pinned to 0.2.0.
2. Hooks stay off until the owner answers; QUIRKWRIGHT_HOME is not set yet.
3. Evergreen refresh due 2026-11-29 (see skills/quirkwright/evergreen.json).
