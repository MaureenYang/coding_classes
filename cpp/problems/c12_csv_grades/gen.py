TITLE = "成績單解析"
TOPIC = "字串/IO"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

import string


def sp(rng):
    return " " * rng.choice([0, 0, 0, 1, 2])


def rand_name(rng):
    parts = ["".join(rng.choice(string.ascii_letters) for _ in range(rng.randint(1, 6))) for _ in range(rng.randint(1, 2))]
    return " ".join(parts)


def rand_line(rng, maxk):
    fields = [sp(rng) + rand_name(rng) + sp(rng)]
    for _ in range(rng.randint(0, maxk)):
        fields.append(sp(rng) + ("" if rng.random() < 0.15 else str(rng.randint(0, 100))) + sp(rng))
    return ",".join(fields)


def fmt(lines):
    return f"{len(lines)}\n" + "\n".join(lines)


def manual_cases():
    return [
        ("sample", fmt(["amy, 90, 80", "  Mary Ann ,100,  , 95", "bob", "cat, 70,"])),
        ("nobody_has_scores", fmt(["a", "b,", "c, ,  ,"])),
        ("trailing_comma_and_empty_fields", fmt(["x,", "y,,", "z, , 50, ,", "w,100,,,0"])),
        ("spaces_everywhere", fmt(["   lots of   spaces   ,   1   ,   2   "])),
        ("zero_and_hundred", fmt(["p,0", "q,100", "r,0,100"])),
        ("repeating_decimals", fmt(["t,1,1,2", "u,100,99,99", "v,2,3,3"])),
        ("max_fields", fmt([",".join(["big"] + [str(i % 101) for i in range(100)])] * 100)),
    ]


def random_case(rng, size):
    n, k = {"small": (5, 4), "medium": (500, 10)}.get(size, (10000, 100))
    return fmt([rand_line(rng, k) for _ in range(n)])
