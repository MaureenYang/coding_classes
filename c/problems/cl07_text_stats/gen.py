TITLE = "文字統計"
TOPIC = "getchar/EOF"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0
RAW_INPUT = True          # 測資結尾不自動補換行：要測「最後一行沒有換行」

import string

VISIBLE = string.ascii_letters + string.digits + string.punctuation


def rand_text(rng, n_words, maxlen, alpha, gaps):
    parts = []
    for _ in range(n_words):
        parts.append("".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen))))
        parts.append(rng.choice(gaps))
    if rng.random() < 0.5 and parts:
        parts.pop()                                   # 有時候最後沒有空白 / 換行
    if rng.random() < 0.2:
        parts.insert(0, rng.choice(gaps))             # 開頭是空白
    return "".join(parts)


def manual_cases():
    return [
        ("sample", "Hello, world!\n  C is   fun.\n"),
        ("empty_input", ""),
        ("only_newlines", "\n\n\n"),
        ("only_spaces_no_newline", "   \t  "),
        ("no_trailing_newline", "abc def\nlast line"),
        ("single_char", "x"),
        ("tabs_and_spaces", "\ta\t\tb  c\t\n\t\n"),
        ("tie_longest_word", "abc xyz pqr\nlmn\n"),
        ("tie_top_letter", "bbb aaa ccc BBB AAA\n"),
        ("no_letters", "123 456 !!! ...\n"),
        ("case_insensitive", "aAaA bB\n"),
        ("longest_line_is_last", "short\na much longer final line"),
        ("blank_lines_between", "one\n\n\ntwo\n\n"),
        ("one_huge_word", "Q" * 1000000),
        ("huge_line_of_words", " ".join(["ab"] * 300000) + "\n"),
    ]


def random_case(rng, size):
    gaps = [" ", " ", "  ", "\t", "\n", "\n", " \n", "\n\n"]
    if size == "small":
        return rand_text(rng, rng.randint(0, 6), 4, "abAB12,.", gaps)
    if size == "medium":
        return rand_text(rng, 3000, 12, VISIBLE, gaps)
    return rand_text(rng, 120000, 10, VISIBLE, gaps)
