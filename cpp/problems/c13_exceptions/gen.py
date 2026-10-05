TITLE = "安全的計算機"
TOPIC = "例外處理"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

MIN, MAX = -2 ** 63, 2 ** 63 - 1
BIN = ["add", "sub", "mul", "div", "mod"]


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def val(rng, small):
    if small:
        return rng.randint(-5, 5)
    return rng.choice([rng.randint(-100, 100), rng.randint(MIN, MAX), MIN, MAX, -1, 0, 1, 2 ** 32, -2 ** 32,
                       3037000499, 3037000500, rng.randint(-10 ** 9, 10 ** 9)])


def manual_cases():
    return [
        ("sample", fmt(["push 7", "add", "push 0", "div", "size", "push 9223372036854775807", "push 1", "add"])),
        ("empty_stack_ops", fmt(["top", "pop", "dup", "add", "size", "push 1", "mul", "top"])),
        ("stack_unchanged_after_error", fmt(["push 5", "push 0", "div", "size", "top", "pop", "top", "mod", "size"])),
        ("llong_min_div_minus_one", fmt(["push -9223372036854775808", "push -1", "div", "size",
                                         "mod", "top", "size"])),
        ("llong_min_mod_minus_one_is_zero", fmt(["push -9223372036854775808", "push -1", "mod", "top",
                                                 "push 7", "push -1", "mod", "top"])),
        ("overflow_boundaries", fmt(["push 9223372036854775807", "push 0", "add", "top",
                                     "push 1", "sub", "top", "push 2", "mul",
                                     "push -9223372036854775808", "push 1", "sub",
                                     "push 3037000499", "dup", "mul", "top",
                                     "push 3037000500", "dup", "mul", "size"])),
        ("negative_div_mod", fmt(["push -7", "push 2", "div", "top", "push -7", "push 2", "mod", "top",
                                  "push 7", "push -2", "mod", "top"])),
        ("many_errors", fmt(["add"] * 100000 + ["push 1"] * 50000 + ["push 0", "div"] * 25000)),
    ]


def random_case(rng, size):
    q = {"small": 15, "medium": 3000}.get(size, 200000)
    small = size == "small"
    ops, n = [], 0
    for _ in range(q):
        r = rng.random()
        if r < 0.4 or n == 0 and r < 0.6:
            ops.append(f"push {val(rng, small)}"); n += 1
        elif r < 0.7:
            ops.append(rng.choice(BIN)); n = max(1, n - 1) if n >= 2 else n
        elif r < 0.78:
            ops.append("dup"); n += n > 0
        elif r < 0.85:
            ops.append("pop"); n = max(0, n - 1)
        elif r < 0.95:
            ops.append("top")
        else:
            ops.append("size")
    return fmt(ops)
