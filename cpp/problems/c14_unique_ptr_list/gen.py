TITLE = "智慧指標串列"
TOPIC = "unique_ptr"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["pushmany 3", "push 10", "print 5", "reverse", "pop", "sum", "size"])),
        ("empty_ops", fmt(["pop", "front", "print 3", "reverse", "sum", "size", "clear", "size"])),
        ("single_element", fmt(["push -5", "reverse", "front", "print 1", "pop", "pop", "print 1"])),
        ("print_more_than_size", fmt(["pushmany 4", "print 100", "print 0", "print 2"])),
        ("sum_needs_long_long", fmt(["push 1000000000"] * 10 + ["push -1000000000"] * 3 + ["sum"])),
        ("clear_then_reuse", fmt(["pushmany 5", "clear", "front", "push 7", "print 3", "size"])),
        ("million_nodes_destructor", fmt(["pushmany 1000000", "size", "front", "sum"])),
        ("million_nodes_clear", fmt(["pushmany 1000000", "clear", "size", "pushmany 1000000", "reverse", "front"])),
    ]


def random_case(rng, size):
    q = {"small": 15, "medium": 3000}.get(size, 200000)
    v = 5 if size == "small" else 10 ** 9
    ops, n, printed = [], 0, 0
    while len(ops) < q:
        r = rng.random()
        if r < 0.4:
            ops.append(f"push {rng.randint(-v, v)}"); n += 1
        elif r < 0.43 and n < 1_500_000:
            k = rng.randint(1, 5 if size == "small" else 3000)
            ops.append(f"pushmany {k}"); n += k
        elif r < 0.6:
            ops.append("pop"); n = max(0, n - 1)
        elif r < 0.65:
            ops.append("front")
        elif r < 0.7 and (size != "large" or rng.random() < 0.01):
            ops.append("reverse")
        elif r < 0.75:
            ops.append("size")
        elif r < 0.8 and (size != "large" or rng.random() < 0.01):
            ops.append("sum")
        elif r < 0.85 and printed < 150000:
            k = rng.randint(0, 6 if size == "small" else 20); printed += k
            ops.append(f"print {k}")
        elif r < 0.86:
            ops.append("clear"); n = 0
    return fmt(ops)
