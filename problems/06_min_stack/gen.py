TITLE = "最小值堆疊"
TOPIC = "Stack"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

LO, HI = -2 ** 31, 2 ** 31 - 1


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["push 3", "push 1", "push 1", "getmin", "pop", "getmin", "pop", "getmin"])),
        ("empty_ops", fmt(["pop", "top", "getmin", "push 5", "pop", "getmin", "top"])),
        ("duplicate_min", fmt(["push 2", "push 2", "push 2", "pop", "getmin", "pop", "getmin", "pop", "getmin"])),
        ("int_limits", fmt([f"push {HI}", f"push {LO}", "getmin", "top", "pop", "getmin", "top",
                            f"push {LO}", f"push {HI}", "getmin", "top"])),
        ("decreasing_then_pop_all", fmt([f"push {x}" for x in range(10, 0, -1)] + ["getmin", "pop"] * 10)),
        ("increasing_300000", fmt([f"push {i}" for i in range(150000)] + ["getmin", "top"] * 75000)),
        ("decreasing_300000", fmt([f"push {-i}" for i in range(150000)] + ["getmin", "pop"] * 75000)),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 3000}.get(size, 300000)
    lo, hi = (-5, 5) if size == "small" else (LO, HI)
    ops, n = [], 0
    for _ in range(q):
        r = rng.random()
        if r < 0.45 or n == 0 and r < 0.8:
            ops.append(f"push {rng.randint(lo, hi)}"); n += 1
        elif r < 0.7:
            ops.append("pop"); n = max(0, n - 1)
        else:
            ops.append(rng.choice(["top", "getmin", "getmin"]))
    return fmt(ops)
