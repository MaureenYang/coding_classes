TITLE = "圖形與多型"
TOPIC = "繼承/多型"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

import math

PI = math.acos(-1.0)


def props(s):
    k = s[0]
    if k == "circle":
        r = s[1]; return PI * r * r, 2 * PI * r
    if k == "rect":
        return s[1] * s[2], 2 * (s[1] + s[2])
    if k == "square":
        return s[1] * s[1], 4 * s[1]
    a, b, c = s[1:]
    p = (a + b + c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c)), a + b + c


def safe(x):
    """四捨五入到兩位小數時，離 .xx5 太近的值可能因不同公式而有差異，避開"""
    frac = (x * 100) % 1
    return abs(frac - 0.5) > 1e-6


def rand_shape(rng, v):
    while True:
        k = rng.choice(["circle", "rect", "square", "triangle"])
        if k == "circle": s = (k, rng.randint(1, v))
        elif k == "rect": s = (k, rng.randint(1, v), rng.randint(1, v))
        elif k == "square": s = (k, rng.randint(1, v))
        else:
            a, b = rng.randint(1, v), rng.randint(1, v)
            lo, hi = abs(a - b) + 1, min(a + b - 1, v)
            if lo > hi:
                continue
            s = (k, a, b, rng.randint(lo, hi))
        if all(safe(x) for x in props(s)):
            return s


def fmt(shapes):
    return f"{len(shapes)}\n" + "\n".join(" ".join(map(str, s)) for s in shapes)


def manual_cases():
    return [
        ("sample", fmt([("rect", 2, 3), ("circle", 1), ("square", 2), ("triangle", 3, 4, 5)])),
        ("single_circle", fmt([("circle", 1000)])),
        ("equal_area_keep_input_order", fmt([("square", 6), ("rect", 4, 9), ("rect", 9, 4), ("rect", 2, 18), ("triangle", 9, 10, 17)])),
        ("square_is_a_rectangle", fmt([("square", 5), ("rect", 5, 5), ("square", 1), ("rect", 1, 1)])),
        ("equilateral_and_tiny", fmt([("triangle", 1, 1, 1), ("triangle", 2, 2, 3), ("circle", 2), ("rect", 1, 1)])),
        ("all_same", fmt([("circle", 3)] * 1000)),
    ]


def random_case(rng, size):
    n, v = {"small": (6, 6), "medium": (2000, 100)}.get(size, (100000, 1000))
    return fmt([rand_shape(rng, v) for _ in range(n)])
