TITLE = "括號配對"
TOPIC = "Stack"
DIFFICULTY = "★☆☆"
TIME_LIMIT = 1.0

PAIRS = ["()", "[]", "{}"]


def fmt(ss):
    return f"{len(ss)}\n" + "\n".join(ss)


def balanced(rng, n):
    """產生長度 n（偶數）的合法括號字串"""
    out, st, opens = [], [], n // 2
    while opens or st:
        if opens and (not st or rng.random() < 0.5):
            p = rng.choice(PAIRS); out.append(p[0]); st.append(p[1]); opens -= 1
        else:
            out.append(st.pop())
    return "".join(out)


def corrupt(rng, s):
    s = list(s)
    i = rng.randrange(len(s))
    s[i] = rng.choice("()[]{}")
    return "".join(s)


def manual_cases():
    return [
        ("sample", fmt(["()", "([]{})", "([)]", "((", ")("])),
        ("single_char", fmt(list("()[]{}"))),
        ("close_first_empty_stack", fmt([")", "]", "}", "())", "())(()", "]["])),
        ("leftover_open", fmt(["(", "(()", "{[()]", "(" * 7])),
        ("mismatch_type", fmt(["(]", "[}", "{)", "([}]", "{[(])}"])),
        ("deep_nesting_100000", fmt(["(" * 50000 + ")" * 50000, "[" * 50000 + "]" * 49999 + ")"])),
        ("many_lines", fmt(["()"] * 500 + ["(("] * 500)),
    ]


def random_case(rng, size):
    t, maxlen = {"small": (5, 8), "medium": (100, 200)}.get(size, (10, 100000))
    ss = []
    for _ in range(t):
        n = rng.randint(1, maxlen // 2) * 2
        s = balanced(rng, n)
        r = rng.random()
        if r < 0.3:
            s = corrupt(rng, s)
        elif r < 0.4:
            s = s[:-1] if len(s) > 1 else s
        ss.append(s)
    return fmt(ss)
