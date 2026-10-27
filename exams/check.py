"""檢查考卷：python3 exams/check.py [路線 ...]

1. 解析每一份考卷，確認格式正確。
2. 題目裡有完整程式（含 main）、答案裡有 ```output 區塊的題目，實際編譯執行，核對輸出。
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "web"))
from exam import load_exam  # noqa: E402

LANG = {"ds": "cpp", "cpp": "cpp", "c": "c", "cii": "c", "ce": "c", "aia": "c"}


def blocks(md, langs):
    return [m.group(2) for m in re.finditer(r"```(\w*)\n(.*?)```", md, re.S) if m.group(1) in langs]


def run(code, lang, tmp):
    if lang == "python":
        src = os.path.join(tmp, "q.py")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        r = subprocess.run([sys.executable, "-I", src], capture_output=True, text=True, timeout=30)
        return (r.stdout, None) if r.returncode == 0 else (None, r.stderr)
    src = os.path.join(tmp, "q." + ("c" if lang == "c" else "cpp"))
    exe = os.path.join(tmp, "q")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)
    cmd = (["gcc", "-std=c11", src, "-o", exe, "-lm"] if lang == "c"
           else ["g++", "-std=c++17", src, "-o", exe])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        return None, r.stderr
    r = subprocess.run([exe], capture_output=True, text=True, timeout=10)
    return r.stdout, None


def main():
    tracks = sys.argv[1:] or [t for t in LANG if os.path.exists(os.path.join(ROOT, "exams", t + ".md"))]
    bad = 0
    for t in tracks:
        ex = load_exam(t)
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            for q in ex["questions"]:
                outs = blocks(q["a"], {"output"})
                progs = [(b, LANG[t]) for b in blocks(q["q"], {"c", "cpp"}) if re.search(r"\bint\s+main\s*\(", b)]
                progs += [(b, "python") for b in blocks(q["q"], {"python"})]
                if not outs:
                    continue
                if len(progs) != 1:
                    print(f"[{t}] {q['id']}: 有 output 區塊，但題目裡的完整程式有 {len(progs)} 個")
                    bad += 1
                    continue
                got, err = run(progs[0][0], progs[0][1], tmp)
                checked += 1
                if err is not None:
                    print(f"[{t}] {q['id']}: 編譯失敗\n{err}")
                    bad += 1
                elif got.rstrip("\n") != outs[0].rstrip("\n"):
                    print(f"[{t}] {q['id']}: 輸出不符\n--- 答案\n{outs[0]}--- 實際\n{got}")
                    bad += 1
        text = open(os.path.join(ROOT, "exams", t + ".md"), encoding="utf-8").read()
        for no, line in enumerate(text.split("\n"), 1):
            if re.match(r"^\s*([-*]|\d+\.)\s+```", line):
                print(f"[{t}] 第 {no} 行：程式碼區塊不能和清單符號寫在同一行，請另起一行（否則會被當成題目分隔失效）")
                bad += 1
        per = {}
        for q in ex["questions"]:
            per[q["chapter"]] = per.get(q["chapter"], 0) + 1
        print(f"[{t}] {ex['title']}：{len(ex['chapters'])} 章、{len(ex['questions'])} 題，"
              f"核對輸出 {checked} 題；每章題數 {per}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
