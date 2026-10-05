"""網頁版：python3 judge.py serve，然後用瀏覽器打開 http://127.0.0.1:8000

只用 Python 標準函式庫。注意：這個伺服器會編譯並執行送進來的 C++ 程式，
所以預設只綁定 127.0.0.1（只有自己的電腦連得到）。
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import judge

WEB_DIR = os.path.dirname(os.path.abspath(__file__))


def track_of(q):
    t = q.get("track") or "ds"
    if t not in judge.TRACKS:
        raise ValueError("bad track")
    return t


def lesson_list(track="ds"):
    out = []
    d = judge.TRACKS[track]["lessons"]
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(d, name), encoding="utf-8") as f:
            first = f.readline().lstrip("# ").strip()
        out.append({"name": name, "title": first})
    return out


def safe_lesson(name, track="ds"):
    if not re.fullmatch(r"[\w\-]+\.md", name or ""):
        raise ValueError("bad lesson name")
    return os.path.join(judge.TRACKS[track]["lessons"], name)


def problem_list(track="ds"):
    prog = judge.load_progress()
    out = []
    for pid in judge.list_problem_ids(track):
        meta = judge.load_meta(pid)
        p = prog.get(pid, {})
        out.append({"id": pid, "title": meta.TITLE, "topic": meta.TOPIC,
                    "difficulty": meta.DIFFICULTY, "solved": p.get("solved", False),
                    "verdict": p.get("verdict"),
                    "started": os.path.exists(judge.workspace_file(pid))})
    return out


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def problem_detail(pid):
    ws = judge.workspace_file(pid)
    code = read(ws) if os.path.exists(ws) else read(judge.problem_path(pid, "template.cpp"))
    meta = judge.load_meta(pid)
    return {"id": pid, "track": judge.problem_track(pid),
            "markdown": read(judge.problem_path(pid, "problem.md")), "code": code,
            "time_limit": getattr(meta, "TIME_LIMIT", 2.0)}


def tests_detail(pid):
    judge.ensure_tests(pid)
    out = []
    for name in judge.list_tests(pid):
        base = os.path.join(judge.tests_dir(pid), name)
        inp, exp = read(base + ".in"), read(base + ".out")
        out.append({"name": name, "input": judge.preview(inp, 40, 3000),
                    "output": judge.preview(exp, 40, 3000),
                    "input_full": inp if len(inp) <= 3000 else None,
                    "size": len(inp)})
    return out


def save_code(pid, code):
    os.makedirs(judge.WORKSPACE_DIR, exist_ok=True)
    with open(judge.workspace_file(pid), "w", encoding="utf-8") as f:
        f.write(code)


def run_code(code, inp, debug):
    try:
        exe = judge.compile_code_string(code, debug)
    except judge.CompileError as e:
        return {"status": "CE", "compile_error": str(e)}
    res = judge.run_exe(exe, inp, 10.0, debug)
    res["stdout"] = res["stdout"][:200000]
    res["stderr"] = res["stderr"][-20000:]
    res["detail"] = judge.describe_returncode(res.get("code"))
    return res


def submit(pid, code, debug):
    save_code(pid, code)
    res = judge.judge_problem(pid, code=code, debug=debug)
    passed = sum(r["verdict"] == "AC" for r in res["results"])
    total = len(judge.list_tests(pid))
    judge.save_progress(pid, res["verdict"], passed, total)
    res["passed"], res["total"] = passed, total
    return res


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path, ctype):
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                return self.send_file(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
            if url.path == "/api/problems":
                return self.send_json(problem_list(track_of(q)))
            if url.path == "/api/problem":
                return self.send_json(problem_detail(judge.resolve_problem(q["id"])))
            if url.path == "/api/tests":
                return self.send_json(tests_detail(judge.resolve_problem(q["id"])))
            if url.path == "/api/lessons":
                return self.send_json(lesson_list(track_of(q)))
            if url.path == "/api/lesson":
                return self.send_json({"markdown": read(safe_lesson(q.get("name"), track_of(q)))})
            self.send_json({"error": "not found"}, 404)
        except (SystemExit, KeyError, ValueError, OSError) as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        url = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            debug = bool(body.get("debug"))
            if url.path == "/api/run":
                return self.send_json(run_code(body.get("code", ""), body.get("input", ""), debug))
            pid = judge.resolve_problem(body.get("id", ""))
            if url.path == "/api/save":
                save_code(pid, body.get("code", ""))
                return self.send_json({"ok": True})
            if url.path == "/api/submit":
                return self.send_json(submit(pid, body.get("code", ""), debug))
            if url.path == "/api/gen":
                seed = body.get("seed")
                n = judge.generate_tests(pid, seed=int(seed) if seed not in (None, "") else None, quiet=True)
                return self.send_json({"ok": True, "count": n})
            if url.path == "/api/reset":
                code = read(judge.problem_path(pid, "template.cpp"))
                save_code(pid, code)
                return self.send_json({"code": code})
            self.send_json({"error": "not found"}, 404)
        except SystemExit as e:
            self.send_json({"error": str(e)}, 400)
        except (ValueError, OSError) as e:
            self.send_json({"error": str(e)}, 400)


def serve(host="127.0.0.1", port=8000):
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"C++ 資料結構練習平台已啟動：http://{host}:{port}  （Ctrl+C 結束）")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已關閉。")
