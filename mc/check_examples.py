"""核對 mc/lessons/*.md 裡的範例：每個 ```python 區塊後面緊接著 ```output 區塊時，
執行程式並比對輸出。用法：python3 mc/check_examples.py [檔名片段 ...]"""
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FENCE = re.compile(r"^```(\w*)\n(.*?)^```\s*$", re.S | re.M)


def blocks(text):
    out = []
    for m in FENCE.finditer(text):
        out.append((m.group(1), m.group(2), m.start(), m.end()))
    return out


def check(path):
    text = open(path, encoding="utf-8").read()
    bad = 0
    n = 0
    bs = blocks(text)
    for i, (lang, code, s, e) in enumerate(bs):
        if lang != "python" or i + 1 >= len(bs):
            continue
        nlang, expect, ns, _ = bs[i + 1]
        if nlang != "output" or text[e:ns].strip():
            continue
        n += 1
        r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=120)
        got = r.stdout.rstrip("\n")
        if r.returncode != 0 or got != expect.rstrip("\n"):
            bad += 1
            line = text[:s].count("\n") + 1
            print(f"✘ {os.path.basename(path)}:{line}")
            print("  expected:\n" + expect)
            print("  got:\n" + got + ("\n" + r.stderr if r.returncode else ""))
    return n, bad


def main():
    files = sorted(glob.glob(os.path.join(HERE, "lessons", "*.md")))
    if len(sys.argv) > 1:
        files = [f for f in files if any(k in os.path.basename(f) for k in sys.argv[1:])]
    total = fails = 0
    for f in files:
        n, bad = check(f)
        total += n
        fails += bad
        print(f"{'✔' if not bad else '✘'} {os.path.basename(f)}：{n} 個範例")
    print(f"共 {total} 個範例，{fails} 個不符")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
