import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "quirkwright", "scripts"))
import qw  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = qw.main(argv)
    return code, json.loads(buf.getvalue())


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def write(self, name, data):
        p = os.path.join(self.d, name)
        with open(p, "wb") as f:
            f.write(data)
        return p

    def test_clean_lf(self):
        code, r = run(["check", self.write("a.py", b"x = 1\ny = 2\n")])
        self.assertEqual(code, 0)
        self.assertTrue(r["ok"])

    def test_control_byte(self):
        # a path with backslash-v written through a non-raw string
        code, r = run(["check", self.write("b.txt", b"D:" + bytes([11]) + b"ideo\n")])
        self.assertEqual(code, 1)
        f = list(r["files"].values())[0]
        self.assertIn("control-bytes", f["issues"])
        self.assertEqual(f["controls"][0]["byte"], 11)

    def test_crlf_and_expect(self):
        p = self.write("c.txt", b"a\r\nb\r\n")
        code, r = run(["check", p])
        self.assertEqual(r["files"][p]["eol"], "crlf")
        self.assertEqual(code, 0)
        code, r = run(["check", "--expect-eol", "lf", p])
        self.assertEqual(code, 1)

    def test_mixed_bom_trailing_lostu(self):
        p = self.write("d.js", b"\xef\xbb\xbfa \r\nb\ns.replace(/</g, 'u003c')\n")
        code, r = run(["check", p])
        f = r["files"][p]
        self.assertEqual(code, 1)
        for issue in ("mixed-eol", "bom", "lost-backslash-u"):
            self.assertIn(issue, f["issues"])
        self.assertEqual(f["trailing_space_lines"], [1])

    def test_escaped_u_not_flagged(self):
        p = self.write("e.js", b"s = '" + bytes([92]) + b"u003c'\n")
        code, r = run(["check", p])
        self.assertEqual(code, 0)

    def test_missing_file(self):
        code, r = run(["check", os.path.join(self.d, "nope")])
        self.assertEqual(code, 1)

    def test_script_is_clean(self):
        code, r = run(["check", qw.__file__])
        self.assertEqual(code, 0, r)


class PidFilterTests(unittest.TestCase):
    rows = [
        {"pid": 10, "name": "python.exe", "start": "s", "cmd": "python render.py --job 7"},
        {"pid": 11, "name": "bash.exe", "start": "s", "cmd": "bash -c until grep -q render.py log; do sleep 5; done"},
        {"pid": 12, "name": "python.exe", "start": "s", "cmd": "python other.py"},
    ]

    def test_excludes_monitor(self):
        hits = qw.filter_procs(self.rows, r"render\.py")
        real = [h for h in hits if "skipped" not in h]
        self.assertEqual([h["pid"] for h in real], [10])
        self.assertEqual(len(hits), 2)

    def test_all_flag(self):
        hits = qw.filter_procs(self.rows, r"render\.py", include_all=True)
        self.assertTrue(all("skipped" not in h for h in hits))


class QuotedExeTests(unittest.TestCase):
    def test_git_bash_quoted_exe_matches_typed_command(self):
        rows = [{"pid": 7, "name": "sleep.exe", "start": "", "cmd": '"C:\\Program Files\\Git\\usr\\bin\\sleep.exe" 60'}]
        self.assertEqual([h["pid"] for h in qw.filter_procs(rows, "sleep 60")], [7])


class WaitTests(unittest.TestCase):
    def setUp(self):
        self.log = os.path.join(tempfile.mkdtemp(), "job.log")

    def append(self, text, delay):
        def go():
            time.sleep(delay)
            with open(self.log, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        threading.Thread(target=go).start()

    def test_stale_fail_ignored_then_done(self):
        with open(self.log, "w", encoding="utf-8") as f:
            f.write("FAILED old run\n")
        self.append("DONE", 0.3)
        code, r = run(["wait", self.log, "--done", "DONE", "--fail", "FAILED", "--deadline", "5", "--interval", "0.1"])
        self.assertEqual((code, r["result"]), (0, "done"))

    def test_new_fail(self):
        self.append("FAILED now", 0.2)
        code, r = run(["wait", self.log, "--done", "DONE", "--fail", "FAILED", "--deadline", "5", "--interval", "0.1"])
        self.assertEqual((code, r["result"]), (1, "failed"))

    def test_deadline(self):
        code, r = run(["wait", self.log, "--done", "DONE", "--fail", "FAILED", "--deadline", "0.3", "--interval", "0.1"])
        self.assertEqual((code, r["result"]), (1, "deadline"))


class DoctorTests(unittest.TestCase):
    def test_runs(self):
        code, r = run(["doctor"])
        self.assertEqual(code, 0)
        for k in ("shells", "python3", "path_headroom", "mcp_case", "warnings"):
            self.assertIn(k, r)

    def test_mcp_case(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "c.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"projects": {"X:/Work/Repo": {}}}, f)
        r = qw.mcp_case("x:/work/repo", p)
        self.assertFalse(r["exact_key"])
        self.assertEqual(r["case_mismatch_keys"], ["X:/Work/Repo"])

    def test_installed_path(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "i.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"plugins": {"demo@mkt": [{"version": "1.1.1", "installPath": "/c/demo/1.1.1"}]}}, f)
        self.assertEqual(qw.installed_path("demo", p)[0]["version"], "1.1.1")


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(sys.platform == "win32", "hidden desktops are Windows only")
class HiddenRunTests(unittest.TestCase):
    def test_window_never_takes_foreground(self):
        try:
            import tkinter  # noqa: F401
        except ImportError:
            self.skipTest("no tkinter")
        src = "import tkinter as t; r=t.Tk(); r.focus_force(); r.after(1500, r.destroy); r.mainloop()"
        code, r = run(["hidden-run", "--timeout", "20", "--", sys.executable, "-c", src])
        self.assertEqual(code, 0, r)
        self.assertEqual(r["result"], "exited")
        self.assertGreaterEqual(r["windows_seen"], 1)
        self.assertFalse(r["took_foreground"])

    def test_timeout_kills_own_tree_and_logs(self):
        log = os.path.join(tempfile.mkdtemp(), "out.log")
        src = "import sys,time; print('started', flush=True); time.sleep(60)"
        code, r = run(["hidden-run", "--timeout", "1.5", "--log", log, "--", sys.executable, "-c", src])
        self.assertEqual(code, 1)
        self.assertEqual(r["result"], "timeout")
        self.assertLess(r["elapsed_s"], 10)
        with open(log, "rb") as f:
            self.assertIn(b"started", f.read())

    def test_exit_code_passes_through(self):
        code, r = run(["hidden-run", "--", sys.executable, "-c", "raise SystemExit(3)"])
        self.assertEqual(code, 1)
        self.assertEqual(r["exit_code"], 3)

    def test_needs_command(self):
        code, r = run(["hidden-run", "--"])
        self.assertEqual(code, 2)


class AutomodeTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.s = os.path.join(self.d, "settings.json")
        with open(self.s, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"theme": "auto", "autoMode": {"allow": ["$defaults", "hand rule"]}}, f)
        self.home = os.environ.get("QUIRKWRIGHT_HOME")
        os.environ["QUIRKWRIGHT_HOME"] = self.d  # no automode.json: values only from --set

    def tearDown(self):
        if self.home is None:
            os.environ.pop("QUIRKWRIGHT_HOME", None)
        else:
            os.environ["QUIRKWRIGHT_HOME"] = self.home

    def am(self, *a):
        return run(["automode", *a, "--settings", self.s])

    def load(self):
        with open(self.s, encoding="utf-8") as f:
            return json.load(f)["autoMode"]["allow"]

    def test_plan_writes_nothing(self):
        code, r = self.am("plan", "all", "--set", "owner=acme")
        self.assertEqual(code, 0)
        self.assertFalse(r["written"])
        self.assertEqual(self.load(), ["$defaults", "hand rule"])
        self.assertIn("own-repo-gh", r["added"])
        self.assertIn("installs", r["missing"])  # needs folders
        self.assertNotIn("publish", r["added"])  # opt-in

    def test_apply_backup_idempotent_revert(self):
        code, r = self.am("apply", "own-repo-gh", "--set", "owner=acme", "--apply")
        self.assertTrue(r["written"])
        self.assertTrue(os.path.isfile(r["backup"]))
        allow = self.load()
        self.assertEqual(allow[:2], ["$defaults", "hand rule"])
        self.assertTrue(any(x.startswith("[qw:own-repo-gh] ") and "acme" in x for x in allow))
        code, r = self.am("apply", "own-repo-gh", "--set", "owner=acme", "--apply")
        self.assertFalse(r["changed"])
        code, r = self.am("revert", "--apply")
        self.assertEqual(self.load(), ["$defaults", "hand rule"])

    def test_opt_in_and_extra_rule(self):
        code, r = self.am("plan", "publish", "--set", "owner=acme", "--rule", "extra text")
        self.assertIn("publish", r["added"])
        self.assertIn("[qw:rule] extra text", r["allow_after"])

    def test_unknown_preset(self):
        code, r = self.am("plan", "nope")
        self.assertEqual(code, 2)
