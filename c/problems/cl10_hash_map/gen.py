TITLE = "字串雜湊表"
TOPIC = "C 實作 ADT"
DIFFICULTY = "★★★★"
TIME_LIMIT = 1.0

import string


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def rand_key(rng, alpha, maxlen):
    return "".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen)))


def rand_ops(rng, q, pool):
    ops = []
    for _ in range(q):
        r = rng.random()
        k = rng.choice(pool)
        if r < 0.35:
            ops.append(f"put {k} {rng.randint(-10 ** 9, 10 ** 9)}")
        elif r < 0.6:
            ops.append(f"get {k}")
        elif r < 0.75:
            ops.append(f"add {k} {rng.randint(-10 ** 9, 10 ** 9)}")
        elif r < 0.92:
            ops.append(f"del {k}")
        else:
            ops.append("size")
    return ops


def manual_cases():
    return [
        ("sample", fmt(["put apple 3", "put pear 5", "get apple", "add apple 10", "add kiwi 7", "get apple", "del pear", "get pear", "size"])),
        ("empty_table", fmt(["get a", "del a", "size", "add a -5", "get a", "size"])),
        ("overwrite", fmt(["put a 1", "put a 2", "put a -3", "get a", "size"])),
        ("delete_then_reinsert", fmt(["put x 1", "del x", "del x", "get x", "put x 2", "get x", "size"])),
        ("prefix_keys", fmt(["put a 1", "put aa 2", "put aaa 3", "get aa", "del a", "get aaa", "get a", "size"])),
        ("long_keys", fmt([f"put {'z' * 20} 1", f"put {'z' * 19}y 2", f"get {'z' * 20}", f"get {'z' * 19}y", "size"])),
        ("growth_past_rehash", fmt([f"put {c}{d} {i}"
                                    for i, (c, d) in enumerate((c, d) for c in string.ascii_lowercase for d in string.ascii_lowercase)]
                                   + ["get aa", "get zz", "get mq", "size"] + [f"del {c}z" for c in string.ascii_lowercase] + ["size", "get az"])),
        ("many_distinct_keys", fmt([f"put {''.join(string.ascii_lowercase[(i // 26 ** p) % 26] for p in range(4))} {i}" for i in range(200000 - 2)]
                                   + ["size", "get aaaa"])),
        ("big_values", fmt(["put a 1000000000"] + ["add a 1000000000"] * 999 + ["get a", "add a -1000000000", "get a"])),
    ]


def random_case(rng, size):
    if size == "small":
        pool = [rand_key(rng, "ab", 2) for _ in range(4)]
        return fmt(rand_ops(rng, 12, pool))
    if size == "medium":
        pool = [rand_key(rng, string.ascii_lowercase, 6) for _ in range(500)]
        return fmt(rand_ops(rng, 5000, pool))
    pool = [rand_key(rng, string.ascii_lowercase, 20) for _ in range(150000)]
    return fmt(rand_ops(rng, 200000, pool))
