TITLE = "泛型堆疊"
TOPIC = "模板"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

TYPES = ["int", "str", "pair"]


def val(rng, t, small):
    w = lambda: "".join(rng.choice("ab" if small else "abcdefghij") for _ in range(rng.randint(1, 3 if small else 5)))
    if t == "int":
        return str(rng.randint(-5, 5) if small else rng.randint(-10 ** 9, 10 ** 9))
    if t == "str":
        return w()
    return f"{rng.randint(-2, 2) if small else rng.randint(-1000, 1000)} {w()}"


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(["int push 5", "int push -2", "str push hi", "pair push 2 b", "pair push 2 a",
                        "int max", "pair sorted", "str pop", "str top"])),
        ("all_empty", fmt([f"{t} {op}" for t in TYPES for op in ["pop", "top", "size", "max", "sorted"]])),
        ("pair_compare_first_then_second", fmt(["pair push 1 z", "pair push 2 a", "pair push 1 a", "pair push -1 zz",
                                                "pair max", "pair sorted", "pair pop", "pair top"])),
        ("string_lexicographic", fmt(["str push b", "str push ab", "str push a", "str push ba", "str push aa",
                                      "str max", "str sorted"])),
        ("int_negative_and_extremes", fmt(["int push -1000000000", "int push 1000000000", "int push 0",
                                           "int max", "int sorted", "int pop", "int pop", "int max"])),
        ("sorted_does_not_modify", fmt(["int push 3", "int push 1", "int push 2", "int sorted", "int top",
                                        "int pop", "int pop", "int pop", "int pop"])),
        ("duplicates", fmt(["str push x"] * 5 + ["str sorted", "str size", "str max"])),
    ]


def random_case(rng, size):
    q = {"small": 15, "medium": 3000}.get(size, 200000)
    small = size == "small"
    ops, sizes, budget = [], {t: 0 for t in TYPES}, 200000
    while len(ops) < q:
        t = rng.choice(TYPES)
        r = rng.random()
        if r < 0.5:
            ops.append(f"{t} push {val(rng, t, small)}"); sizes[t] += 1
        elif r < 0.7:
            ops.append(f"{t} pop"); sizes[t] = max(0, sizes[t] - 1)
        elif r < 0.8:
            ops.append(f"{t} top")
        elif r < 0.88:
            ops.append(f"{t} size")
        elif r < 0.97:
            ops.append(f"{t} max")
        elif sizes[t] <= budget and (small or rng.random() < 0.02):
            budget -= sizes[t]
            ops.append(f"{t} sorted")
    return fmt(ops)
