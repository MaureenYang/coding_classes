"""考卷檔（exams/<路線>.md）的解析器。

格式（標記都要寫在行首，而且不在程式碼區塊裡面）：

    # 考卷標題
    > 說明文字（可以多行）

    @@@ 07 | 動態記憶體            ← 章節：編號 | 名稱（編號要和教學檔名的開頭相同）
    ??? 預測輸出                   ← 一題開始，後面是題型
    題目（Markdown）
    !!!                            ← 以下是答案
    答案與解說（Markdown）

答案裡用 ```output 包起來的區塊，是題目程式的「標準輸出」，exams/check.py 會實際編譯執行來核對。
"""
import os
import re

EXAM_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exams")


def exam_path(track):
    return os.path.join(EXAM_DIR, f"{track}.md")


def parse_exam(text):
    title, intro, chapters, questions = "", [], [], []
    chapter, q, part = None, None, None
    fence = None
    for line in text.split("\n"):
        stripped = line.strip()
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            if fence is None:
                fence = m.group(1)[0] * len(m.group(1))
            elif stripped.startswith(fence) and stripped.strip(fence[0]) == "":
                fence = None
        if fence is None and not m:
            if line.startswith("@@@ "):
                no, _, name = line[4:].partition("|")
                chapter = {"no": no.strip(), "title": name.strip()}
                chapters.append(chapter)
                q = None
                continue
            if line.startswith("??? "):
                if chapter is None:
                    raise ValueError("題目出現在第一個章節（@@@）之前")
                q = {"chapter": chapter["no"], "type": line[4:].strip(), "q": [], "a": []}
                q["id"] = f"{chapter['no']}-{sum(x['chapter'] == chapter['no'] for x in questions) + 1}"
                questions.append(q)
                part = "q"
                continue
            if line.strip() == "!!!" and q is not None:
                part = "a"
                continue
            if q is None and chapter is None:
                if line.startswith("# ") and not title:
                    title = line[2:].strip()
                elif line.startswith(">"):
                    intro.append(line.lstrip("> ").rstrip())
                continue
        if q is not None:
            q[part].append(line)
    for x in questions:
        x["q"] = "\n".join(x["q"]).strip()
        x["a"] = "\n".join(x["a"]).strip()
        if not x["q"] or not x["a"]:
            raise ValueError(f"題目 {x['id']} 缺少題目或答案")
    return {"title": title, "intro": "\n".join(intro).strip(), "chapters": chapters, "questions": questions}


def load_exam(track):
    with open(exam_path(track), encoding="utf-8") as f:
        return parse_exam(f.read())
