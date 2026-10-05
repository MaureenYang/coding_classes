#!/usr/bin/env python3
"""C++ 資料結構練習平台 — 本機評測工具 (Online-Judge style)

常用指令：
    python3 judge.py list                     列出所有題目與進度
    python3 judge.py show   <題目>            顯示題目敘述
    python3 judge.py start  <題目>            複製樣板到 workspace/<題目>.cpp
    python3 judge.py gen    <題目> [--seed S] 產生測資（含 corner case + 隨機測資）
    python3 judge.py test   <題目> [檔案]     編譯並跑全部測資，回報 AC/WA/TLE/RE
    python3 judge.py stress <題目> [檔案]     對拍：隨機小測資和標準解比對，找出反例
    python3 judge.py run    <檔案> [輸入檔]   單純編譯並執行你的程式
    python3 judge.py serve  [--port 8000]     啟動網頁版（瀏覽器寫 code、跑測資）

<題目> 可以寫完整名稱 (03_my_vector)、編號 (3) 或名稱 (my_vector)。
加上 --debug 會用 -fsanitize=address,undefined 編譯，可抓出越界、記憶體錯誤。
"""
import argparse
import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_DIR = os.path.join(ROOT, "problems")
LESSONS_DIR = os.path.join(ROOT, "lessons")

# 兩條學習路線：資料結構 (ds) 與 C++ 深入 (cpp)，各自有教學與題目資料夾
TRACKS = {
    "ds": {"name": "資料結構", "lessons": LESSONS_DIR, "problems": PROBLEMS_DIR},
    "cpp": {"name": "C++ 深入", "lessons": os.path.join(ROOT, "cpp", "lessons"),
            "problems": os.path.join(ROOT, "cpp", "problems")},
}
WORKSPACE_DIR = os.path.join(ROOT, "workspace")
BUILD_DIR = os.path.join(ROOT, ".build")
PROGRESS_FILE = os.path.join(ROOT, ".progress.json")

CXX = os.environ.get("CXX", "g++")
BASE_FLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Wno-unused-result", "-Wno-unused-parameter"]
RELEASE_FLAGS = ["-O2"]
DEBUG_FLAGS = ["-g", "-O1", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
               "-D_GLIBCXX_DEBUG"]
MEMORY_LIMIT_MB = 512

# 預設隨機測資數量
RANDOM_PLAN = [("small", 6), ("medium", 3), ("large", 2)]

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color(text, code):
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def green(t): return color(t, "32;1")
def red(t): return color(t, "31;1")
def yellow(t): return color(t, "33;1")
def cyan(t): return color(t, "36")
def dim(t): return color(t, "2")


VERDICT_COLOR = {"AC": green, "WA": red, "TLE": yellow, "RE": red, "MLE": red, "CE": yellow}


# ---------------------------------------------------------------- problems --

def list_problem_ids(track=None):
    ids = []
    for key, t in TRACKS.items():
        if track and key != track:
            continue
        d = t["problems"]
        if os.path.isdir(d):
            ids += sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, "gen.py")))
    return ids


def problem_track(pid):
    for key, t in TRACKS.items():
        if os.path.isfile(os.path.join(t["problems"], pid, "gen.py")):
            return key
    return None


def resolve_problem(name):
    ids = list_problem_ids()
    if name in ids:
        return name
    m = re.fullmatch(r"([cC]?)(\d+)", name)
    if m:  # 3 → 03_my_vector；c7 → c07_fraction
        prefix = m.group(1).lower()
        for pid in ids:
            head = pid.split("_", 1)[0]
            if head[:len(prefix)] == prefix and head[len(prefix):].isdigit() \
                    and head[len(prefix):].lstrip("0") == m.group(2).lstrip("0"):
                return pid
    matches = [pid for pid in ids if pid.split("_", 1)[-1] == name] or \
              [pid for pid in ids if name in pid]
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise SystemExit(f"題目名稱 '{name}' 不明確，可能是：{', '.join(matches)}")
    raise SystemExit(f"找不到題目 '{name}'。用 `python3 judge.py list` 看所有題目。")


def load_meta(pid):
    path = problem_path(pid, "gen.py")
    spec = importlib.util.spec_from_file_location(f"gen_{pid}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def problem_path(pid, *parts):
    track = problem_track(pid) or "ds"
    return os.path.join(TRACKS[track]["problems"], pid, *parts)


def workspace_file(pid):
    return os.path.join(WORKSPACE_DIR, f"{pid}.cpp")


def load_progress():
    try:
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_progress(pid, verdict, passed, total):
    prog = load_progress()
    old = prog.get(pid, {})
    prog[pid] = {
        "verdict": verdict,
        "passed": passed,
        "total": total,
        "solved": old.get("solved", False) or verdict == "AC",
        "time": time.strftime("%Y-%m-%d %H:%M"),
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------- compile --

class CompileError(Exception):
    pass


def compile_cpp(src, debug=False):
    """編譯 C++ 檔案，回傳執行檔路徑；同樣內容不會重複編譯。"""
    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(src, "rb") as f:
        code = f.read()
    flags = BASE_FLAGS + (DEBUG_FLAGS if debug else RELEASE_FLAGS)
    key = hashlib.sha1(code + " ".join(flags).encode()).hexdigest()[:16]
    exe = os.path.join(BUILD_DIR, f"{key}.out")
    if os.path.exists(exe):
        return exe
    proc = subprocess.run([CXX, *flags, src, "-o", exe + ".tmp"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise CompileError(proc.stderr)
    os.replace(exe + ".tmp", exe)
    if proc.stderr.strip():
        # 編譯警告也很重要，例如「沒有 return」、「比較 signed/unsigned」
        sys.stderr.write(yellow("[編譯警告]\n") + proc.stderr + "\n")
    return exe


def compile_code_string(code, debug=False):
    os.makedirs(BUILD_DIR, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix=".cpp", dir=BUILD_DIR)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        return compile_cpp(path, debug)
    except CompileError as e:
        raise CompileError(str(e).replace(path, "main.cpp")) from None
    finally:
        os.unlink(path)


def reference_exe(pid):
    return compile_cpp(problem_path(pid, "solution.cpp"))


# --------------------------------------------------------------------- run --

def _limits(debug):
    def apply():
        try:
            import resource
            if not debug:  # AddressSanitizer 需要很大的虛擬記憶體，debug 模式不限制
                lim = MEMORY_LIMIT_MB * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
        except (ImportError, ValueError, OSError):
            pass
    return apply


def run_exe(exe, input_text, time_limit=2.0, debug=False):
    """執行程式，回傳 dict(status, stdout, stderr, time)。status: OK / TLE / RE"""
    start = time.perf_counter()
    try:
        proc = subprocess.run([exe], input=input_text.encode(), capture_output=True,
                              timeout=time_limit, preexec_fn=_limits(debug))
    except subprocess.TimeoutExpired as e:
        return {"status": "TLE", "stdout": (e.stdout or b"").decode(errors="replace"),
                "stderr": "", "time": time.perf_counter() - start, "code": None}
    elapsed = time.perf_counter() - start
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    if proc.returncode != 0:
        status = "RE"
        if "bad_alloc" in err or "std::length_error" in err:
            status = "MLE"
        return {"status": status, "stdout": out, "stderr": err, "time": elapsed,
                "code": proc.returncode}
    return {"status": "OK", "stdout": out, "stderr": err, "time": elapsed, "code": 0}


def describe_returncode(code):
    if not code:
        return ""
    if code < 0:
        import signal
        try:
            name = signal.Signals(-code).name
        except ValueError:
            name = str(-code)
        hint = {"SIGSEGV": "記憶體存取錯誤：陣列越界、空指標、遞迴太深（stack overflow）？",
                "SIGABRT": "程式被中止：assert 失敗、記憶體不足、或 STL 偵測到錯誤？",
                "SIGFPE": "算術錯誤：除以 0 或 mod 0？",
                "SIGKILL": "被強制終止：可能用太多記憶體？"}.get(name, "")
        return f"收到訊號 {name}。{hint}"
    return f"main 回傳 {code}（不是 0）"


def normalize(text):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def compare(expected, got):
    """逐行比較（忽略行尾空白與結尾空行）。回傳 None 表示相同，否則回傳差異說明。"""
    exp, out = normalize(expected), normalize(got)
    for i in range(max(len(exp), len(out))):
        e = exp[i] if i < len(exp) else None
        g = out[i] if i < len(out) else None
        if e != g:
            return {"line": i + 1, "expected": e, "got": g,
                    "expected_lines": len(exp), "got_lines": len(out)}
    return None


def preview(text, max_lines=12, max_chars=600):
    lines = text.split("\n")
    shown = "\n".join(lines[:max_lines])
    if len(shown) > max_chars:
        shown = shown[:max_chars] + " ..."
    elif len(lines) > max_lines:
        shown += f"\n... (共 {len(lines)} 行)"
    return shown


# ------------------------------------------------------------------- tests --

def tests_dir(pid):
    return problem_path(pid, "tests")


def list_tests(pid):
    d = tests_dir(pid)
    if not os.path.isdir(d):
        return []
    names = sorted(f[:-3] for f in os.listdir(d) if f.endswith(".in"))
    return [n for n in names if os.path.exists(os.path.join(d, n + ".out"))]


def generate_tests(pid, seed=None, quiet=False, plan=None):
    meta = load_meta(pid)
    if seed is None:
        seed = getattr(meta, "SEED", 20240101)
    plan = plan or getattr(meta, "RANDOM_PLAN", RANDOM_PLAN)
    rng = random.Random(seed)
    cases = [(f"corner_{name}", text) for name, text in meta.manual_cases()]
    for size, count in plan:
        for i in range(count):
            cases.append((f"random_{size}_{i + 1}", meta.random_case(rng, size)))

    d = tests_dir(pid)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    ref = reference_exe(pid)
    tl = max(10.0, getattr(meta, "TIME_LIMIT", 2.0) * 5)
    for idx, (name, text) in enumerate(cases, 1):
        if not text.endswith("\n"):
            text += "\n"
        base = f"{idx:02d}_{name}"
        res = run_exe(ref, text, tl)
        if res["status"] != "OK":
            raise SystemExit(f"標準解在測資 {base} 執行失敗：{res['status']}\n{res['stderr']}")
        with open(os.path.join(d, base + ".in"), "w", encoding="utf-8") as f:
            f.write(text)
        with open(os.path.join(d, base + ".out"), "w", encoding="utf-8") as f:
            f.write(res["stdout"])
    if not quiet:
        print(green(f"已產生 {len(cases)} 筆測資") + f" → {os.path.relpath(d, ROOT)}/  (seed={seed})")
        for idx, (name, text) in enumerate(cases, 1):
            size = len(text)
            print(f"  {idx:02d}_{name:<28} {dim(f'{size:,} bytes')}")
    return len(cases)


def ensure_tests(pid):
    if not list_tests(pid):
        generate_tests(pid, quiet=True)


def judge_problem(pid, src=None, code=None, debug=False, stop_on_fail=False, on_result=None):
    """跑所有測資，回傳 dict(verdict, results, compile_error)。"""
    meta = load_meta(pid)
    tl = getattr(meta, "TIME_LIMIT", 2.0) * (4 if debug else 1)
    ensure_tests(pid)
    try:
        exe = compile_code_string(code, debug) if code is not None else compile_cpp(src, debug)
    except CompileError as e:
        return {"verdict": "CE", "results": [], "compile_error": str(e)}
    results = []
    final = "AC"
    for name in list_tests(pid):
        with open(os.path.join(tests_dir(pid), name + ".in"), encoding="utf-8") as f:
            inp = f.read()
        with open(os.path.join(tests_dir(pid), name + ".out"), encoding="utf-8") as f:
            exp = f.read()
        res = run_exe(exe, inp, tl, debug)
        r = {"name": name, "time": round(res["time"], 3), "verdict": None, "detail": None,
             "input": preview(inp)}
        if res["status"] == "TLE":
            r["verdict"] = "TLE"
            r["detail"] = f"超過時間限制 {tl:g} 秒"
        elif res["status"] in ("RE", "MLE"):
            r["verdict"] = res["status"]
            r["detail"] = describe_returncode(res["code"])
            r["stderr"] = res["stderr"][-3000:]
        else:
            diff = compare(exp, res["stdout"])
            if diff is None:
                r["verdict"] = "AC"
            else:
                r["verdict"] = "WA"
                r["detail"] = diff
                r["expected"] = preview(exp)
                r["got"] = preview(res["stdout"])
        results.append(r)
        if on_result:
            on_result(r)
        if r["verdict"] != "AC" and final == "AC":
            final = r["verdict"]
            if stop_on_fail:
                break
    return {"verdict": final, "results": results, "compile_error": None}


# ---------------------------------------------------------------- commands --

def pick_source(pid, path):
    if path:
        return path
    ws = workspace_file(pid)
    if os.path.exists(ws):
        return ws
    raise SystemExit(f"找不到你的程式。先執行 `python3 judge.py start {pid}`，"
                     f"或指定檔案：`python3 judge.py test {pid} my.cpp`")


def print_failure(r, debug=False):
    v = r["verdict"]
    print(f"\n{VERDICT_COLOR[v]('── ' + r['name'] + ' : ' + v + ' ──')}")
    print(cyan("輸入：")); print(r["input"])
    if v == "WA":
        d = r["detail"]
        print(cyan(f"第 {d['line']} 行不同："))
        print(f"  預期：{d['expected'] if d['expected'] is not None else '(沒有這一行)'}")
        print(f"  你的：{d['got'] if d['got'] is not None else '(沒有這一行)'}")
        print(dim(f"  （預期共 {d['expected_lines']} 行，你輸出 {d['got_lines']} 行）"))
    else:
        print(r["detail"])
        if r.get("stderr"):
            print(cyan("stderr：")); print(r["stderr"])
        if v == "RE" and not debug:
            print(dim("提示：加上 --debug 重新執行，可以看到更詳細的錯誤位置。"))


def cmd_list(args):
    prog = load_progress()
    for key, t in TRACKS.items():
        ids = list_problem_ids(key)
        if not ids:
            continue
        print(cyan(f"\n【{t['name']}】"))
        print(f"{'題目':<26}{'主題':<16}{'難度':<8}狀態")
        print("-" * 64)
        for pid in ids:
            meta = load_meta(pid)
            p = prog.get(pid)
            if p and p.get("solved"):
                status = green("✔ 已通過")
            elif p:
                status = red(f"✘ {p['verdict']} ({p['passed']}/{p['total']})")
            elif os.path.exists(workspace_file(pid)):
                status = yellow("… 作答中")
            else:
                status = dim("未開始")
            print(f"{pid:<26}{meta.TOPIC:<14}{meta.DIFFICULTY:<6}{status}")
    print(dim("\n教學在 lessons/（資料結構）與 cpp/lessons/（C++ 深入）。"))
    print(dim("題目可用編號指定：3 → 03_my_vector，c7 → C++ 深入第 7 題。"))


def cmd_show(args):
    pid = resolve_problem(args.problem)
    with open(problem_path(pid, "problem.md"), encoding="utf-8") as f:
        print(f.read())


def cmd_start(args):
    pid = resolve_problem(args.problem)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    dst = workspace_file(pid)
    if os.path.exists(dst) and not args.force:
        print(f"{os.path.relpath(dst, ROOT)} 已存在（加 --force 會覆蓋）。")
    else:
        shutil.copy(problem_path(pid, "template.cpp"), dst)
        print(green("已建立 ") + os.path.relpath(dst, ROOT))
    print(f"題目：problems/{pid}/problem.md")
    print(f"寫完後執行：python3 judge.py test {pid}")


def cmd_gen(args):
    pid = resolve_problem(args.problem)
    generate_tests(pid, seed=args.seed)


def cmd_test(args):
    pid = resolve_problem(args.problem)
    src = pick_source(pid, args.file)
    print(f"評測 {cyan(pid)}  檔案 {os.path.relpath(os.path.abspath(src), ROOT)}"
          + (yellow("  [debug 模式]") if args.debug else ""))

    def show(r):
        v = r["verdict"]
        print(f"  {r['name']:<34} {VERDICT_COLOR[v](v):<4} {dim(str(r['time']) + 's')}")

    res = judge_problem(pid, src=src, debug=args.debug, on_result=show)
    if res["verdict"] == "CE":
        print(yellow("編譯錯誤 (CE)："))
        print(res["compile_error"])
        save_progress(pid, "CE", 0, len(list_tests(pid)))
        return 1
    results = res["results"]
    passed = sum(r["verdict"] == "AC" for r in results)
    fails = [r for r in results if r["verdict"] != "AC"]
    for r in fails[:args.show]:
        print_failure(r, args.debug)
    print()
    if not fails:
        print(green(f"全部通過！AC {passed}/{len(results)}  🎉"))
    else:
        print(VERDICT_COLOR[res["verdict"]](f"{res['verdict']}：通過 {passed}/{len(results)}"))
        corner = [r["name"] for r in fails if "corner" in r["name"]]
        if corner:
            print(dim("沒過的 corner case 名稱就是提示，想想看那個邊界情況你有沒有處理。"))
        print(dim(f"找不到錯？試試對拍：python3 judge.py stress {pid}"))
    save_progress(pid, res["verdict"], passed, len(results))
    return 0 if not fails else 1


def cmd_stress(args):
    pid = resolve_problem(args.problem)
    src = pick_source(pid, args.file)
    meta = load_meta(pid)
    try:
        mine = compile_cpp(src, args.debug)
    except CompileError as e:
        print(yellow("編譯錯誤 (CE)：")); print(e); return 1
    ref = reference_exe(pid)
    tl = getattr(meta, "TIME_LIMIT", 2.0) * (4 if args.debug else 1) + 1
    seed = args.seed if args.seed is not None else random.randrange(1 << 30)
    rng = random.Random(seed)
    print(f"對拍 {cyan(pid)}：最多 {args.n} 筆隨機小測資 (seed={seed})")
    for i in range(1, args.n + 1):
        inp = meta.random_case(rng, "small")
        if not inp.endswith("\n"):
            inp += "\n"
        exp = run_exe(ref, inp, 10)["stdout"]
        got = run_exe(mine, inp, tl, args.debug)
        bad = got["status"] != "OK" or compare(exp, got["stdout"]) is not None
        if bad:
            print(red(f"\n第 {i} 筆找到反例！"))
            print(cyan("輸入：")); print(preview(inp, 30, 2000))
            if got["status"] != "OK":
                print(f"你的程式：{got['status']} {describe_returncode(got.get('code'))}")
                if got["stderr"]:
                    print(got["stderr"][-2000:])
            else:
                d = compare(exp, got["stdout"])
                print(cyan(f"第 {d['line']} 行不同："))
                print(f"  預期：{d['expected']}")
                print(f"  你的：{d['got']}")
            os.makedirs(WORKSPACE_DIR, exist_ok=True)
            fail_in = os.path.join(WORKSPACE_DIR, f"{pid}.failed.in")
            with open(fail_in, "w", encoding="utf-8") as f:
                f.write(inp)
            print(dim(f"反例已存到 {os.path.relpath(fail_in, ROOT)}，"
                      f"可用 python3 judge.py run {os.path.relpath(src, ROOT)} {os.path.relpath(fail_in, ROOT)} 重現"))
            return 1
        if i % 50 == 0:
            print(dim(f"  已比對 {i} 筆..."))
    print(green(f"{args.n} 筆隨機測資全部和標準解一致。"))
    return 0


def cmd_run(args):
    try:
        exe = compile_cpp(args.file, args.debug)
    except CompileError as e:
        print(yellow("編譯錯誤 (CE)：")); print(e); return 1
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            data = f.read()
        res = run_exe(exe, data, args.time, args.debug)
        sys.stdout.write(res["stdout"])
        sys.stderr.write(res["stderr"])
        print(dim(f"\n[{res['status']}  {res['time']:.3f}s] {describe_returncode(res.get('code'))}"),
              file=sys.stderr)
        return 0 if res["status"] == "OK" else 1
    print(dim("（直接輸入資料，Ctrl+D 結束輸入）"), file=sys.stderr)
    return subprocess.call([exe])


def cmd_serve(args):
    from web.server import serve
    serve(args.host, args.port)


def main(argv=None):
    p = argparse.ArgumentParser(description="C++ 資料結構練習平台",
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="列出題目"); s.set_defaults(func=cmd_list)
    s = sub.add_parser("show", help="顯示題目"); s.add_argument("problem"); s.set_defaults(func=cmd_show)
    s = sub.add_parser("start", help="建立作答檔")
    s.add_argument("problem"); s.add_argument("--force", action="store_true"); s.set_defaults(func=cmd_start)
    s = sub.add_parser("gen", help="產生測資")
    s.add_argument("problem"); s.add_argument("--seed", type=int); s.set_defaults(func=cmd_gen)
    s = sub.add_parser("test", help="評測")
    s.add_argument("problem"); s.add_argument("file", nargs="?")
    s.add_argument("--debug", action="store_true", help="用 sanitizer 編譯，抓記憶體錯誤")
    s.add_argument("--show", type=int, default=1, help="顯示幾筆失敗測資的細節")
    s.set_defaults(func=cmd_test)
    s = sub.add_parser("stress", help="對拍")
    s.add_argument("problem"); s.add_argument("file", nargs="?")
    s.add_argument("-n", type=int, default=300); s.add_argument("--seed", type=int)
    s.add_argument("--debug", action="store_true"); s.set_defaults(func=cmd_stress)
    s = sub.add_parser("run", help="編譯並執行")
    s.add_argument("file"); s.add_argument("input", nargs="?")
    s.add_argument("--time", type=float, default=10.0)
    s.add_argument("--debug", action="store_true"); s.set_defaults(func=cmd_run)
    s = sub.add_parser("serve", help="網頁版")
    s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=cmd_serve)

    args = p.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
