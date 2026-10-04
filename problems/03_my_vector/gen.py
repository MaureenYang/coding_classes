TITLE = "自己做一個 vector"
TOPIC = "動態陣列"
DIFFICULTY = "★☆☆"
TIME_LIMIT = 2.0

BIG = 10 ** 9


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["capacity", "push 5", "push 7", "push 9", "capacity", "get 2", "get 3", "pop", "size"])),
        ("pop_empty", fmt(["pop", "pop", "size", "capacity", "get 0", "set 0 1"])),
        ("negative_index", fmt(["push 1", "get -1", "set -1 5", "get -2147483648", "get 2147483647", "get 0"])),
        ("capacity_growth", fmt([op for i in range(20) for op in (f"push {i}", "capacity")])),
        ("pop_keeps_capacity", fmt(["push 1"] * 5 + ["pop"] * 6 + ["size", "capacity", "push 9", "get 0", "capacity"])),
        ("extreme_values", fmt([f"push {BIG}", f"push {-BIG}", "get 0", "get 1", f"set 0 {-BIG}", "get 0"])),
        ("push_200000", fmt([f"push {i}" for i in range(199997)] + ["size", "capacity", "get 199996"])),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 2000}.get(size, 200000)
    ops, n = [], 0
    for _ in range(q):
        r = rng.random()
        if r < 0.4:
            ops.append(f"push {rng.randint(-BIG, BIG)}"); n += 1
        elif r < 0.55:
            ops.append("pop"); n = max(0, n - 1)
        elif r < 0.75:
            ops.append(f"get {rng.randint(-2, n + 1)}")
        elif r < 0.9:
            ops.append(f"set {rng.randint(-2, n + 1)} {rng.randint(-BIG, BIG)}")
        else:
            ops.append(rng.choice(["size", "capacity"]))
    return fmt(ops)
