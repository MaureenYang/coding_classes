TITLE = "單向鏈結串列"
TOPIC = "鏈結串列"
DIFFICULTY = "★★☆"
TIME_LIMIT = 2.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["push_back 1", "push_back 2", "push_front 0", "print", "insert 1 9", "print",
                        "erase 0", "reverse", "print", "erase 5"])),
        ("empty_ops", fmt(["print", "size", "pop_front", "pop_back", "erase 0", "reverse", "print", "insert 1 5", "insert -1 5"])),
        ("tail_after_pop_back", fmt(["push_back 1", "push_back 2", "pop_back", "push_back 3", "print",
                                     "pop_back", "pop_back", "push_back 4", "print", "size"])),
        ("tail_after_erase_last", fmt(["push_back 1", "push_back 2", "push_back 3", "erase 2", "push_back 9", "print",
                                       "erase 0", "erase 0", "erase 0", "print", "push_back 7", "push_front 6", "print"])),
        ("tail_after_reverse", fmt(["push_back 1", "push_back 2", "push_back 3", "reverse", "push_back 0", "print",
                                    "reverse", "pop_back", "push_back 5", "print"])),
        ("insert_at_size", fmt(["insert 0 1", "insert 1 2", "insert 2 3", "insert 4 9", "print", "insert 3 4", "print"])),
        ("single_element", fmt(["push_front 42", "reverse", "print", "pop_back", "print", "push_back 1", "pop_front", "size", "print"])),
        ("long_list_reverse", fmt([f"push_back {i}" for i in range(4000)] + ["reverse"] * 3 + ["pop_back"] * 3 + ["size", "print"])),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 500}.get(size, 5000)
    ops, n = [], 0
    for _ in range(q):
        r = rng.random()
        x = rng.randint(-10 ** 9, 10 ** 9) if size != "small" else rng.randint(0, 9)
        if r < 0.2:
            ops.append(f"push_front {x}"); n += 1
        elif r < 0.4:
            ops.append(f"push_back {x}"); n += 1
        elif r < 0.5:
            ops.append("pop_front"); n = max(0, n - 1)
        elif r < 0.6:
            ops.append("pop_back"); n = max(0, n - 1)
        elif r < 0.7:
            i = rng.randint(-1, n + 1)
            ops.append(f"insert {i} {x}"); n += 0 <= i <= n
        elif r < 0.8:
            i = rng.randint(-1, n)
            ops.append(f"erase {i}"); n -= 0 <= i < n
        elif r < 0.85:
            ops.append("reverse")
        elif r < (0.95 if size != "large" else 0.86):
            ops.append("print")
        else:
            ops.append("size")
    return fmt(ops)
