TITLE = "動態陣列"
TOPIC = "malloc/realloc"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def rand_ops(rng, q, max_shift, val):
    ops, size, shifts = [], 0, 0
    for _ in range(q):
        r = rng.random()
        bad = rng.random() < 0.1
        idx = lambda hi: rng.choice([-1, hi, hi + 5, -1000000000000]) if bad or hi <= 0 else rng.randrange(hi)
        if r < 0.35:
            ops.append(f"push {rng.randint(-val, val)}"); size += 1
        elif r < 0.45:
            ops.append("pop"); size = max(0, size - 1)
        elif r < 0.6:
            ops.append(f"get {idx(size)}")
        elif r < 0.68:
            ops.append(f"set {idx(size)} {rng.randint(-val, val)}")
        elif r < 0.74 and shifts < max_shift:
            i = rng.choice([-1, size + 1]) if bad else rng.randint(0, size)
            ops.append(f"insert {i} {rng.randint(-val, val)}"); shifts += 1
            if 0 <= i <= size: size += 1
        elif r < 0.8 and shifts < max_shift:
            i = idx(size); ops.append(f"erase {i}"); shifts += 1
            if 0 <= i < size: size -= 1
        elif r < 0.86:
            ops.append(rng.choice(["size", "cap"]))
        elif r < 0.88:
            ops.append("clear"); size = 0
        elif size <= 50:
            ops.append("print")
        else:
            ops.append("cap")
    return ops


def manual_cases():
    return [
        ("sample", fmt(["cap", "push 10", "push 20", "push 30", "cap", "insert 0 5", "print", "erase 2", "get 7", "pop", "size"])),
        ("empty_ops", fmt(["pop", "print", "get 0", "set 0 1", "erase 0", "insert 1 5", "insert -1 5", "size", "cap"])),
        ("capacity_doubling", fmt(sum([[f"push {i}", "cap"] for i in range(17)], []))),
        ("pop_does_not_shrink", fmt(["push 1", "push 2", "push 3", "pop", "pop", "pop", "cap", "pop", "push 9", "cap", "print"])),
        ("insert_at_ends", fmt(["insert 0 2", "insert 0 1", "insert 2 3", "insert 3 4", "print", "cap", "insert 5 9", "erase 3", "erase 0", "print"])),
        ("clear_then_reuse", fmt(["push 1", "push 2", "push 3", "clear", "size", "cap", "print", "push 7", "cap", "print", "clear", "clear"])),
        ("huge_index", fmt(["push 1", "get 1000000000000", "get -1000000000000", "set 1 5", "erase 1", "insert 2 0", "get 0"])),
        ("extreme_values", fmt(["push 1000000000", "push -1000000000", "set 0 -1000000000", "print", "pop", "pop"])),
        ("many_pushes", fmt([f"push {i}" for i in range(100000 - 3)] + ["size", "cap", "get 99996"])),
    ]


def random_case(rng, size):
    q = {"small": 12, "medium": 3000}.get(size, 100000)
    return fmt(rand_ops(rng, q, 2000, {"small": 9}.get(size, 10 ** 9)))
