import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hooks"))
import guards  # noqa: E402

BS = chr(92)


class KillTests(unittest.TestCase):
    def test_blocks_image_kills(self):
        for cmd in ("taskkill /F /IM python.exe", "taskkill //F //IM node.exe",
                    "Stop-Process -Name python -Force", "pkill -f python3", "killall node"):
            self.assertIsNotNone(guards.kill_verdict(cmd), cmd)

    def test_allows_pid_kills(self):
        for cmd in ("taskkill /F /PID 9520", "Stop-Process -Id 9520", "kill 1234", "echo python"):
            self.assertIsNone(guards.kill_verdict(cmd), cmd)


class HeredocTests(unittest.TestCase):
    def test_warns(self):
        cmd = "cat > a.py <<'EOF'" + chr(10) + "p = 'C:" + BS + BS + "x'" + chr(10) + "EOF"
        self.assertIsNotNone(guards.heredoc_verdict(cmd))

    def test_quiet_without_backslash(self):
        cmd = "cat > a.py <<'EOF'" + chr(10) + "print(1)" + chr(10) + "EOF"
        self.assertIsNone(guards.heredoc_verdict(cmd))

    def test_quiet_for_non_python(self):
        cmd = "cat > a.txt <<'EOF'" + chr(10) + "a" + BS + "b" + chr(10) + "EOF"
        self.assertIsNone(guards.heredoc_verdict(cmd))


class OffByDefault(unittest.TestCase):
    def test_no_active_hooks_json(self):
        self.assertFalse(os.path.exists(os.path.join(HERE, "..", "hooks", "hooks.json")))


if __name__ == "__main__":
    unittest.main()
