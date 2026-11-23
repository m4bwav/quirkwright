#!/usr/bin/env python3
"""qw.py - Windows host checks for coding agents (stdlib, Python 3.9+).

Commands (each prints one JSON object):
  check <files...>                 byte damage: CR, control bytes, BOM, lost backslash-u, trailing spaces
  pid <pattern> [--all]            real Windows pid(s) of processes whose command line matches
  wait --done RE --fail RE --deadline S <log>   wait for success or NEW failure lines, with a deadline
  hidden-run [--timeout S] [--log F] -- <cmd...>   run on a hidden desktop: its windows never take focus
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


# ---------- hidden-run ----------
# Runs a command on a fresh Win32 desktop (CreateDesktopW + STARTUPINFO.lpDesktop) so its windows
# never take the mouse, keyboard or foreground from the user. Children inherit the desktop. A job
# object holds the process tree: on timeout only what this call started is killed.

def _hidden_run_win(cmdline, timeout, log_path):
    import ctypes
    import ctypes.wintypes as W
    import msvcrt

    u32 = ctypes.WinDLL("user32", use_last_error=True)
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class STARTUPINFO(ctypes.Structure):
        _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                    ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD), ("dwXSize", W.DWORD),
                    ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD), ("dwYCountChars", W.DWORD),
                    ("dwFillAttribute", W.DWORD), ("dwFlags", W.DWORD), ("wShowWindow", W.WORD),
                    ("cbReserved2", W.WORD), ("lpReserved2", ctypes.c_void_p), ("hStdInput", W.HANDLE),
                    ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]

    class PROCINFO(ctypes.Structure):
        _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE), ("dwProcessId", W.DWORD),
                    ("dwThreadId", W.DWORD)]

    class BASIC_LIMIT(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", W.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", W.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", W.DWORD), ("SchedulingClass", W.DWORD)]

    class EXT_LIMIT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC_LIMIT), ("IoInfo", ctypes.c_uint64 * 6),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    u32.CreateDesktopW.restype = W.HANDLE
    u32.GetForegroundWindow.restype = W.HWND
    k32.CreateJobObjectW.restype = W.HANDLE
    enum_proc = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)

    name = "qw-hidden-%d-%d" % (os.getpid(), int(time.time() * 1000) % 100000)
    hdesk = u32.CreateDesktopW(name, None, None, 0, 0x10000000, None)  # GENERIC_ALL
    if not hdesk:
        return {"ok": False, "error": "CreateDesktopW failed", "winerror": ctypes.get_last_error()}, 1
    job = k32.CreateJobObjectW(None, None)
    info = EXT_LIMIT()
    info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))

    log_f = open(log_path, "ab") if log_path else None
    out_fd = log_f.fileno() if log_f else sys.stderr.fileno()
    h_out = msvcrt.get_osfhandle(out_fd)
    os.set_handle_inheritable(h_out, True)
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = name
    si.dwFlags = 0x100  # STARTF_USESTDHANDLES
    si.hStdInput = None
    si.hStdOutput = h_out
    si.hStdError = h_out
    pi = PROCINFO()
    fg_before = u32.GetForegroundWindow()
    start = time.time()
    created = k32.CreateProcessW(None, ctypes.create_unicode_buffer(cmdline), None, None, True,
                                 0x4, None, None, ctypes.byref(si), ctypes.byref(pi))  # CREATE_SUSPENDED
    if not created:
        err = ctypes.get_last_error()
        u32.CloseDesktop(hdesk)
        k32.CloseHandle(job)
        if log_f:
            log_f.close()
        return {"ok": False, "error": "CreateProcessW failed", "winerror": err, "cmd": cmdline}, 1
    k32.AssignProcessToJobObject(job, pi.hProcess)
    k32.ResumeThread(pi.hThread)

    seen = set()
    took_fg = False

    def cb(hwnd, _):
        if u32.IsWindowVisible(hwnd):
            seen.add(hwnd)
        return True

    cb_ref = enum_proc(cb)
    result = "exited"
    while True:
        if k32.WaitForSingleObject(pi.hProcess, 200) == 0:
            break
        u32.EnumDesktopWindows(hdesk, cb_ref, 0)
        fg = u32.GetForegroundWindow()
        if fg and fg != fg_before:
            pid = W.DWORD()
            u32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
            if pid.value == pi.dwProcessId:
                took_fg = True
        if timeout and time.time() - start >= timeout:
            result = "timeout"
            k32.TerminateJobObject(job, 1)  # only the tree this call started
            k32.WaitForSingleObject(pi.hProcess, 5000)
            break
    code = W.DWORD()
    k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code))
    k32.CloseHandle(pi.hThread)
    k32.CloseHandle(pi.hProcess)
    k32.CloseHandle(job)  # kill-on-close ends any children the command left behind
    u32.CloseDesktop(hdesk)
    if log_f:
        log_f.close()
    rep = {"ok": result == "exited" and code.value == 0, "result": result, "exit_code": code.value,
           "pid": pi.dwProcessId, "desktop": name, "elapsed_s": round(time.time() - start, 2),
           "windows_seen": len(seen), "took_foreground": took_fg, "cmd": cmdline}
    if result == "exited" and not seen and time.time() - start < 1:
        rep["hint"] = ("exited fast with no window: Store/packaged apps (new Notepad, Calculator) hand off "
                       "to the default desktop or fail here; use a classic Win32 exe")
    return rep, 0 if rep["ok"] else 1


def cmd_hidden_run(args):
    cmd = list(args.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        return out({"ok": False, "error": "give a command after --"}, 2)
    if sys.platform != "win32":
        return out({"ok": False, "error": "hidden-run needs Windows (CreateDesktopW)"}, 2)
    rep, code = _hidden_run_win(subprocess.list2cmdline(cmd), args.timeout, args.log)
    return out(rep, code)


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
    h = sub.add_parser("hidden-run", help="run a command on a hidden desktop so windows never steal focus")
    h.add_argument("--timeout", type=float, help="kill the command's process tree after S seconds")
    h.add_argument("--log", help="append the command's stdout and stderr here (default: stderr)")
    h.add_argument("command", nargs=argparse.REMAINDER)
    d = sub.add_parser("doctor")
    d.add_argument("--plugin")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    return {"check": cmd_check, "pid": cmd_pid, "wait": cmd_wait, "doctor": cmd_doctor,
            "hidden-run": cmd_hidden_run}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
