#!/usr/bin/env python3
"""qw.py - Windows host checks for coding agents (stdlib, Python 3.9+).

Commands (each prints one JSON object):
  check <files...>                 byte damage: CR, control bytes, BOM, lost backslash-u, trailing spaces
  pid <pattern> [--all]            real Windows pid(s) of processes whose command line matches
  wait --done RE --fail RE --deadline S <log>   wait for success or NEW failure lines, with a deadline
  doctor [--plugin NAME]           shell tools, python3 stub, cwd case vs MCP keys, path headroom, installPath

Exit codes: 0 ok, 1 findings / failure / timeout, 2 usage error.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

BS = chr(92)
CONTROL_OK = {9, 10, 13}


def out(obj, code=0):
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    return code


# ---------- check ----------

def check_bytes(data):
    cr = data.count(13)
    lf = data.count(10)
    crlf = data.count(b"\r\n")
    controls = []
    for i, b in enumerate(data):
        if b < 32 and b not in CONTROL_OK:
            line = data.count(10, 0, i) + 1
            controls.append({"line": line, "byte": b})
    bom = data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    trailing = [n + 1 for n, ln in enumerate(lines) if ln != ln.rstrip(" \t")]
    # A decoded escape cannot be told apart from intent, so report escapes that look
    # half-decoded: 'u00' plus two hex digits with no backslash in front.
    lost_u = [n + 1 for n, ln in enumerate(lines) if re.search(r"(?<![\\\w])u00[0-9a-fA-F]{2}\b", ln)]
    mixed = cr > 0 and crlf not in (0, lf)
    issues = []
    if controls:
        issues.append("control-bytes")
    if mixed:
        issues.append("mixed-eol")
    if bom:
        issues.append("bom")
    if lost_u:
        issues.append("lost-backslash-u")
    return {
        "cr": cr,
        "lf": lf,
        "eol": "none" if lf == 0 else ("crlf" if crlf == lf else ("lf" if cr == 0 else "mixed")),
        "controls": controls[:20],
        "bom": bom,
        "trailing_space_lines": trailing[:20],
        "lost_backslash_u_lines": lost_u[:20],
        "issues": issues,
    }


def cmd_check(args):
    results = {}
    bad = False
    for p in args.files:
        try:
            with open(p, "rb") as f:
                data = f.read()
        except OSError as e:
            results[p] = {"error": str(e)}
            bad = True
            continue
        r = check_bytes(data)
        if args.expect_eol and r["eol"] not in ("none", args.expect_eol):
            r["issues"].append("eol-not-" + args.expect_eol)
        results[p] = r
        bad = bad or bool(r["issues"])
    return out({"ok": not bad, "files": results}, 1 if bad else 0)


# ---------- pid ----------

def list_processes():
    """Return [{pid, name, start, cmd}] using CIM on Windows, ps elsewhere."""
    if os.name == "nt":
        ps = shutil.which("pwsh") or shutil.which("powershell")
        if not ps:
            return None
        script = ("Get-CimInstance Win32_Process | Select-Object ProcessId,Name,"
                  "@{n='Start';e={$_.CreationDate.ToString('s')}},CommandLine | ConvertTo-Json -Compress")
        r = subprocess.run([ps, "-NoProfile", "-Command", script], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        rows = json.loads(r.stdout or "[]")
        if isinstance(rows, dict):
            rows = [rows]
        return [{"pid": x.get("ProcessId"), "name": x.get("Name"), "start": x.get("Start"),
                 "cmd": x.get("CommandLine") or ""} for x in rows]
    r = subprocess.run(["ps", "-eo", "pid=,lstart=,args="], capture_output=True, text=True)
    rows = []
    for ln in r.stdout.splitlines():
        parts = ln.split(None, 6)
        if len(parts) < 7:
            continue
        rows.append({"pid": int(parts[0]), "name": os.path.basename(parts[6].split()[0]),
                     "start": " ".join(parts[1:6]), "cmd": parts[6]})
    return rows


MONITOR_HINTS = ("until ", "while ", "Monitor", "tail -f", "Get-Content -Wait")


def normalize_cmd(cmd):
    """'"C:\\...\\sleep.exe" 60' -> 'sleep 60', so a pattern matches how the command was typed."""
    m = re.match(r'\s*"([^"]+)"(.*)$', cmd) or re.match(r'\s*(\S+)(.*)$', cmd)
    if not m:
        return cmd
    exe = re.split(r"[\\/]", m.group(1))[-1]
    if exe.lower().endswith(".exe"):
        exe = exe[:-4]
    return exe + m.group(2)


def filter_procs(rows, pattern, include_all=False, self_pid=None):
    rx = re.compile(pattern)
    hits = []
    for p in rows:
        if p["pid"] == self_pid:
            continue
        cmd = p.get("cmd") or ""
        if not (rx.search(cmd) or rx.search(normalize_cmd(cmd))):
            continue
        if "qw.py" in cmd and " pid " in cmd:
            continue
        looks_monitor = any(h in cmd for h in MONITOR_HINTS)
        if looks_monitor and not include_all:
            p = dict(p, skipped="looks like a wait loop or Monitor")
        hits.append(p)
    return hits


def cmd_pid(args):
    rows = list_processes()
    if rows is None:
        return out({"ok": False, "error": "no PowerShell found to query CIM"}, 1)
    hits = filter_procs(rows, args.pattern, args.all, os.getpid())
    real = [h for h in hits if "skipped" not in h]
    return out({"ok": bool(real), "pattern": args.pattern, "matches": real,
                "skipped": [h for h in hits if "skipped" in h],
                "note": "kill only these pids, after checking start time; never by image name"},
               0 if real else 1)


# ---------- wait ----------

def count_matches(path, rx):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for ln in f if rx.search(ln))
    except FileNotFoundError:
        return 0


def cmd_wait(args):
    done = re.compile(args.done)
    fail = re.compile(args.fail)
    base_done = count_matches(args.log, done) if args.new_only else 0
    base_fail = count_matches(args.log, fail)
    start = time.time()
    while True:
        d = count_matches(args.log, done)
        f = count_matches(args.log, fail)
        waited = round(time.time() - start, 1)
        if f > base_fail:
            return out({"ok": False, "result": "failed", "new_fail_lines": f - base_fail, "waited_s": waited}, 1)
        if d > base_done:
            return out({"ok": True, "result": "done", "waited_s": waited}, 0)
        if time.time() - start >= args.deadline:
            return out({"ok": False, "result": "deadline", "waited_s": waited,
                        "hint": "check the job is alive (qw.py pid) before waiting again"}, 1)
        time.sleep(args.interval)


# ---------- doctor ----------

def python3_stub():
    p = shutil.which("python3")
    if not p:
        return {"present": False}
    stub = "WindowsApps" in p
    return {"present": True, "path": p, "store_stub": stub}


def mcp_case(cwd, claude_json):
    try:
        with open(claude_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"checked": False}
    keys = list((data.get("projects") or {}).keys())
    norm = lambda s: s.replace(BS, "/").rstrip("/")
    c = norm(cwd)
    exact = [k for k in keys if norm(k) == c]
    folded = [k for k in keys if norm(k).lower() == c.lower() and norm(k) != c]
    return {"checked": True, "exact_key": bool(exact), "case_mismatch_keys": folded}


def installed_path(name, plugins_json):
    try:
        with open(plugins_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    found = []
    for key, entries in (data.get("plugins") or {}).items():
        if key.split("@")[0] != name:
            continue
        for e in entries if isinstance(entries, list) else [entries]:
            found.append({"key": key, "version": e.get("version"), "installPath": e.get("installPath")})
    return found


def cmd_doctor(args):
    home = os.path.expanduser("~")
    cwd = os.getcwd()
    rep = {
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "stdout_encoding": sys.stdout.encoding,
        "shells": {n: bool(shutil.which(n)) for n in ("bash", "pwsh", "powershell", "py")},
        "msys": bool(os.environ.get("MSYSTEM")),
        "python3": python3_stub(),
        "cwd": cwd,
        "cwd_len": len(cwd),
        "path_headroom": 259 - len(cwd),
        "mcp_case": mcp_case(cwd, os.path.join(home, ".claude.json")),
    }
    if args.plugin:
        rep["plugin"] = installed_path(args.plugin, os.path.join(home, ".claude", "plugins", "installed_plugins.json"))
    warn = []
    if rep["python3"].get("store_stub"):
        warn.append("python3 is the Store stub: use python or py -3")
    if rep["path_headroom"] < 110:
        warn.append("cwd is deep: clones and builds here may pass 260 chars")
    if rep["mcp_case"].get("case_mismatch_keys"):
        warn.append("MCP project key differs from cwd only by case: local MCP servers will not load")
    if (rep["stdout_encoding"] or "").lower() not in ("utf-8", "utf8"):
        warn.append("stdout is not UTF-8: set PYTHONIOENCODING=utf-8 or reconfigure")
    rep["warnings"] = warn
    return out(rep, 0)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="qw.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("files", nargs="+")
    c.add_argument("--expect-eol", choices=("lf", "crlf"))
    p = sub.add_parser("pid")
    p.add_argument("pattern")
    p.add_argument("--all", action="store_true", help="include wait loops and monitors")
    w = sub.add_parser("wait")
    w.add_argument("log")
    w.add_argument("--done", required=True)
    w.add_argument("--fail", required=True)
    w.add_argument("--deadline", type=float, required=True)
    w.add_argument("--interval", type=float, default=5.0)
    w.add_argument("--new-only", action="store_true", help="ignore done lines already in the log")
    d = sub.add_parser("doctor")
    d.add_argument("--plugin")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    return {"check": cmd_check, "pid": cmd_pid, "wait": cmd_wait, "doctor": cmd_doctor}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
