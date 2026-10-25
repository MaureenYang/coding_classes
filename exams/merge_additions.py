"""把新增的題目加到考卷每一章的最後面：python3 exams/merge_additions.py <考卷.md> <新增題目.md>

新增題目檔用和考卷一樣的格式，以 `@@@ <章節編號>` 分段（章名可省略）。
題目加在該章現有題目的後面，所以既有題目的編號（作答紀錄用的 id）不會改變。
"""
import re
import sys


def split_chapters(text):
    """回傳 [(章節編號, 該章的所有行)]，第一段（章節之前）的編號是 None。"""
    parts, cur_no, cur = [], None, []
    fence = None
    for line in text.split("\n"):
        m = re.match(r"^(`{3,})", line.strip())
        if m:
            fence = None if fence and line.strip().startswith(fence) else (fence or m.group(1))
        if fence is None and line.startswith("@@@ "):
            parts.append((cur_no, cur))
            cur_no, cur = line[4:].split("|")[0].strip(), []
        cur.append(line)
    parts.append((cur_no, cur))
    return parts


def main():
    exam_path, add_path = sys.argv[1], sys.argv[2]
    exam = split_chapters(open(exam_path, encoding="utf-8").read())
    adds = {no: lines[1:] for no, lines in split_chapters(open(add_path, encoding="utf-8").read()) if no}
    known = {no for no, _ in exam if no}
    unknown = set(adds) - known
    if unknown:
        sys.exit(f"新增檔裡有考卷沒有的章節：{sorted(unknown)}")
    out = []
    for no, lines in exam:
        while lines and lines[-1].strip() == "":
            lines = lines[:-1]
        out.extend(lines)
        if no in adds:
            out.append("")
            body = adds[no]
            while body and body[0].strip() == "":
                body = body[1:]
            while body and body[-1].strip() == "":
                body = body[:-1]
            out.extend(body)
        out.append("")
    with open(exam_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip("\n") + "\n")


if __name__ == "__main__":
    main()
