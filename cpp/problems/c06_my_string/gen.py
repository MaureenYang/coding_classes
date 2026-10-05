TITLE = "自己做一個字串類別"
TOPIC = "RAII/五法則"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

LIMIT = 10 ** 4


def fmt(k, ops):
    return f"{k} {len(ops)}\n" + "\n".join(ops)


def simulate_ops(rng, k, q, wordlen, print_limit):
    s = [""] * k
    ops = []
    while len(ops) < q:
        r = rng.random()
        i, j = rng.randrange(k), rng.randrange(k)
        if rng.random() < 0.15:
            j = i                                     # 刻意製造自我操作
        if r < 0.2:
            w = "".join(rng.choice("abc") for _ in range(rng.randint(1, wordlen)))
            ops.append(f"set {i} {w}"); s[i] = w
        elif r < 0.35:
            ops.append(f"copy {i} {j}"); s[i] = s[j]
        elif r < 0.5:
            ops.append(f"move {i} {j}")
            if i != j:
                s[i], s[j] = s[j], ""
        elif r < 0.65:
            if len(s[i]) + len(s[j]) > LIMIT:
                continue
            ops.append(f"append {i} {j}"); s[i] = s[i] + s[j]
        elif r < 0.75:
            ops.append(f"swap {i} {j}"); s[i], s[j] = s[j], s[i]
        elif r < 0.9 and len(s[i]) <= print_limit:
            ops.append(f"print {i}")
        else:
            ops.append(f"len {i}")
    return ops


def manual_cases():
    return [
        ("sample", fmt(3, ["set 0 hello", "copy 1 0", "append 1 1", "print 1", "move 2 0", "print 0", "len 2", "print 2"])),
        ("all_empty", fmt(2, ["print 0", "len 1", "copy 0 1", "move 1 0", "append 0 1", "swap 0 1", "print 0"])),
        ("self_copy", fmt(1, ["set 0 abc", "copy 0 0", "print 0", "copy 0 0", "len 0"])),
        ("self_move", fmt(1, ["set 0 abc", "move 0 0", "print 0", "len 0"])),
        ("self_append_doubles", fmt(1, ["set 0 ab"] + ["append 0 0", "print 0"] * 5 + ["len 0"])),
        ("moved_from_is_empty", fmt(2, ["set 0 xyz", "move 1 0", "print 0", "len 0", "print 1", "append 0 1", "print 0"])),
        ("swap_uses_move", fmt(3, ["set 0 left", "set 1 right", "swap 0 1", "print 0", "print 1", "swap 2 0", "print 2", "print 0"])),
        ("overwrite_many_times_leak", fmt(1, [f"set 0 {'a' * (i % 20 + 1)}" for i in range(100000)] + ["len 0"])),
        ("copy_chain", fmt(10, ["set 0 seed"] + [f"copy {i + 1} {i}" for i in range(9)] + [f"print {i}" for i in range(10)])),
    ]


def random_case(rng, size):
    k = {"small": rng.randint(1, 3), "medium": rng.randint(1, 10)}.get(size, 10)
    q = {"small": 15, "medium": 3000}.get(size, 200000)
    return fmt(k, simulate_ops(rng, k, q, 5 if size == "small" else 20, 60 if size != "small" else LIMIT))
