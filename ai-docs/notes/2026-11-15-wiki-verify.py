"""Run the qw.py examples the wiki shows and print each output, for wikiwright outputs/diffout.

usage: python wiki-verify.py QW_PY WORK_DIR > wiki-verify.out.txt
WORK_DIR is a fresh scratch folder; fixture files are written there.
"""
import json, subprocess, sys
from pathlib import Path

qw, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
work.mkdir(parents=True, exist_ok=True)
BS = chr(92)
(work / "good.py").write_bytes(b"print('hi')\n")
(work / "crlf.py").write_bytes(b"print('hi')\r\nprint('bye')\r\n")
(work / "bom.md").write_bytes(b"\xef\xbb\xbf# Title\n")
(work / "esc.py").write_bytes(b"path = 'C:\x0colder\x08in'\n")
(work / "job.log").write_bytes(b"step 1\nstep 2\nDONE\n")
(work / "bad.log").write_bytes(b"step 1\nTraceback (most recent call last):\n")


def run(label, *args):
    p = subprocess.run([sys.executable, str(qw), *args], cwd=work, capture_output=True, text=True)
    print("== " + label)
    out = p.stdout.strip()
    try:
        out = json.dumps(json.loads(out), indent=2)
    except ValueError:
        pass
    print("$ python qw.py " + " ".join(args))
    print(out)
    print("exit " + str(p.returncode))
    print()


run("check-good", "check", "good.py", "--expect-eol", "lf")
run("check-crlf", "check", "crlf.py", "--expect-eol", "lf")
run("check-bom", "check", "bom.md")
run("check-escape", "check", "esc.py")
run("wait-done", "wait", "job.log", "--done", "DONE", "--fail", "Traceback|ERROR", "--deadline", "5")
run("wait-old-fail-line", "wait", "bad.log", "--done", "DONE", "--fail", "Traceback|ERROR", "--deadline", "2", "--interval", "1")
(work / "run.log").write_bytes(b"step 1\n")
import threading, time
def append_later():
    time.sleep(1.5)
    with open(work / "run.log", "ab") as f:
        f.write(b"ERROR: out of memory\n")
threading.Thread(target=append_later).start()
run("wait-new-fail-line", "wait", "run.log", "--done", "DONE", "--fail", "Traceback|ERROR", "--deadline", "10", "--interval", "1")
run("wait-deadline", "wait", "bad.log", "--done", "DONE", "--fail", "NEVER", "--deadline", "2", "--interval", "1")
run("pid-none", "pid", "no-such-command-xyz 123")

guards = qw.parents[3] / "hooks" / "guards.py"


def hook(label, mode, tool_input):
    p = subprocess.run([sys.executable, str(guards), mode], input=json.dumps({"tool_input": tool_input}),
                       cwd=work, capture_output=True, text=True)
    print("== " + label)
    print((p.stdout + p.stderr).strip().replace(str(work), "<work>"))
    print("exit " + str(p.returncode))
    print()


hook("hook-kill-image", "kill", {"command": "taskkill /F /IM python.exe"})
hook("hook-kill-name", "kill", {"command": "Stop-Process -Name node"})
hook("hook-kill-pid", "kill", {"command": "taskkill /F /PID 1234"})
hook("hook-check-crlf", "check", {"file_path": "crlf.py"})
hook("hook-check-escape", "check", {"file_path": "esc.py"})
hook("hook-check-bom", "check", {"file_path": "bom.md"})
hook("hook-check-good", "check", {"file_path": "good.py"})
