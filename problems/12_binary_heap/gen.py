TITLE = "二元堆積"
TOPIC = "Heap"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

E18 = 10 ** 18
Q = 500000


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["push 5", "push 2", "push 8", "top", "pop", "pop", "size"])),
        ("empty_ops", fmt(["pop", "top", "size", "push 1", "pop", "pop", "top"])),
        ("duplicates", fmt(["push 3"] * 5 + ["push 1", "push 3"] + ["pop"] * 8)),
        ("only_left_child", fmt(["push 1", "push 3", "push 2", "pop", "pop", "pop"])),
        ("extremes", fmt([f"push {E18}", f"push {-E18}", "push 0", "pop", "pop", "pop", "pop"])),
        ("heap_sort_small", fmt([f"push {x}" for x in [9, 4, 7, 1, 8, 2, 6, 3, 5, 0]] + ["pop"] * 10)),
        ("big_increasing", fmt([f"push {i}" for i in range(Q // 2)] + ["pop"] * (Q // 2))),
        ("big_decreasing", fmt([f"push {Q - i}" for i in range(Q // 2)] + ["pop"] * (Q // 2))),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 3000}.get(size, Q)
    v = 5 if size == "small" else E18
    ops, n = [], 0
    for _ in range(q):
        r = rng.random()
        if r < 0.5:
            ops.append(f"push {rng.randint(-v, v)}"); n += 1
        elif r < 0.85:
            ops.append("pop"); n = max(0, n - 1)
        else:
            ops.append(rng.choice(["top", "size"]))
    return fmt(ops)
