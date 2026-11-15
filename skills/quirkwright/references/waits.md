# Long waits and background jobs

Checked: Claude Code 2.1.x, Git Bash, 2026-11-15.

| Quirk | Rule | Repro |
|---|---|---|
| Foreground `sleep` is refused and a Monitor watch expires after about 5 minutes. | Monitor for waits under 5 min; longer ones run `qw.py wait` with `run_in_background`. | `sleep 240` in the foreground |
| A loop that matches only success hangs forever when the job fails (one such loop idled a GPU for 5 hours). | Match done OR failed, with a deadline about twice the expected time: `qw.py wait <log> --done RE --fail RE --deadline S`. On deadline, check the job's pid before waiting again. Never end a turn on one notice. | none (needs a failing job) |
| Old failure lines in a reused log wake the loop at once; grepping JSON for "fail" matches `"failed": []`. | `qw.py wait` counts failure lines at start and waits for growth; parse status JSON instead of grepping it. | `echo '{"failed": []}' \| grep -c fail` gives 1 |

Hand-written loop, when `qw.py` is not at hand:

```bash
base=$(grep -c FAILED job.log); end=$((SECONDS+3600))
until grep -q DONE job.log || [ "$(grep -c FAILED job.log)" -gt "$base" ] || [ $SECONDS -gt $end ]; do sleep 30; done
```
