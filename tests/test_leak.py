"""Fails if a private term appears in a public file.

Terms come from <QUIRKWRIGHT_HOME>/leak-terms.txt (one per line, # comments) when that
folder exists; otherwise from the small generic list below. Every tracked file is
checked, ai-docs/ included; working notes that name the owner live in the sidecar.
"""
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE_DIRS = (".git/",)
GENERIC = ["192.168.", "C:/Users/", "/home/", "/Users/", "@gmail.com", "BEGIN PRIVATE KEY"]
ALLOW_FILES = {"tests/test_leak.py"}


def load_terms():
    home = os.environ.get("QUIRKWRIGHT_HOME")
    if home:
        p = os.path.join(home, "leak-terms.txt")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                terms = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
            return terms, "sidecar"
    return GENERIC, "generic"


def public_files():
    try:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, text=True, check=True)
        files = r.stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        files = []
        for d, _, fs in os.walk(ROOT):
            for f in fs:
                files.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    return [f for f in files if not f.startswith(EXCLUDE_DIRS) and f not in ALLOW_FILES
            and "__pycache__/" not in f and not f.endswith(".pyc")]


class LeakTest(unittest.TestCase):
    def test_no_private_terms(self):
        terms, source = load_terms()
        hits = []
        for rel in public_files():
            try:
                with open(os.path.join(ROOT, rel), "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            low = text.lower()
            for t in terms:
                if t.lower() in low:
                    hits.append("%s: %s" % (rel, t))
        self.assertEqual(hits, [], "private terms (%s list) in public files" % source)


if __name__ == "__main__":
    unittest.main()
