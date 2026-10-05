TITLE = "分數類別"
TOPIC = "運算子多載"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

E9 = 10 ** 9


def frac(rng, v):
    p = rng.randint(-v, v)
    if rng.random() < 0.25:
        return str(p)
    q = 0
    while q == 0:
        q = rng.randint(-v, v)
    return f"{p}/{q}"


def fmt(lines):
    return f"{len(lines)}\n" + "\n".join(lines)


def manual_cases():
    return [
        ("sample", fmt(["1/2 + 1/3", "3/-6 * 2", "0/5 - 7", "1/2 / 0", "-1/2 < 1/-3", "2/4 == 1/2"])),
        ("normalize_sign", fmt(["3/-6 + 0", "-3/-6 + 0", "-3/6 + 0", "0/-5 + 0", "5/1 + 0", "-10/5 + 0"])),
        ("zero_results", fmt(["1/2 - 1/2", "0 * 5/7", "0/3 / 5", "-0 + 0", "0/9 == 0", "0/-9 == 0/4"])),
        ("divide_by_zero", fmt(["1 / 0", "1 / 0/5", "0 / 0/-3", "5/7 / 1/2 ", "3 / 2/4"])),
        ("compare_negative_denominators", fmt(["1/-2 < 1/3", "-1/2 < -1/3", "-1/3 < -1/2", "1/2 < 1/2", "2/-4 == -1/2",
                                               "1/3 == 2/6", "1/3 == 1/4"])),
        ("big_values_long_long", fmt([f"{E9}/{E9 - 1} + {E9 - 1}/{E9}", f"{E9}/{E9 - 1} * {E9 - 1}/{E9}",
                                      f"-{E9}/1 - {E9}/1", f"1/{E9} - 1/{E9 - 1}", f"{E9} * {E9}",
                                      f"1/{E9} / {E9}", f"{E9}/{E9 - 1} < {E9 - 1}/{E9 - 2}"])),
        ("integer_results", fmt(["4/2 + 0", "1/2 + 1/2", "3/4 * 4", "6/3 / 2", "-7/7 - 0"])),
    ]


def random_case(rng, size):
    t, v = {"small": (10, 6), "medium": (2000, 1000)}.get(size, (100000, E9))
    ops = ["+", "-", "*", "/", "<", "=="]
    lines = []
    for _ in range(t):
        a, b, op = frac(rng, v), frac(rng, v), rng.choice(ops)
        if op == "/" and rng.random() < 0.05:
            b = "0"
        lines.append(f"{a} {op} {b}")
    return fmt(lines)
