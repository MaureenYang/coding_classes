TITLE = "自己做一個雜湊表"
TOPIC = "Hash Table"
DIFFICULTY = "★★☆"
TIME_LIMIT = 2.0

E18 = 10 ** 18
Q = 200000


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def put_then_get(keys, rng):
    ops = [f"put {k} {rng.randint(-E18, E18)}" for k in keys]
    ops += [f"get {k}" for k in keys]
    return ops[:Q - 1] + ["size"]


def manual_cases():
    import random
    rng = random.Random(7)
    half = Q // 2
    return [
        ("sample", fmt(["put 5 100", "put -3 7", "get 5", "put 5 1", "get 5", "erase 4", "erase -3", "size"])),
        ("empty_table", fmt(["get 0", "erase 0", "size"])),
        ("negative_keys", fmt(["put -1 1", "put -1000000000000000000 2", "put -7 3",
                               "get -1", "get -1000000000000000000", "get -7", "get 7", "erase -7", "get -7", "size"])),
        ("extreme_keys_and_values", fmt([f"put {E18} {-E18}", f"put {-E18} {E18}", "put 0 0",
                                         f"get {E18}", f"get {-E18}", "get 0", "size"])),
        ("overwrite_keeps_size", fmt(["put 1 1", "put 1 2", "put 1 3", "size", "get 1", "erase 1", "erase 1", "size", "put 1 4", "get 1", "size"])),
        ("anti_power_of_two", fmt(put_then_get([i << 20 for i in range(half)], rng))),
        ("anti_prime_buckets", fmt(put_then_get([i * 1000003 for i in range(half // 2)] +
                                                [i * 100003 + 1 for i in range(half // 2)], rng))),
        ("anti_multiples_of_1e9_7", fmt(put_then_get([i * 1000000007 for i in range(half)], rng))),
        ("erase_heavy", fmt([f"put {i} {i}" for i in range(half)] + [f"erase {i}" for i in range(0, Q - half - 1)] + ["size"])),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 3000}.get(size, Q)
    keyspace = {"small": 5, "medium": 500}.get(size, 50000)
    keys = [rng.randint(-E18, E18) for _ in range(keyspace)]
    ops = []
    for _ in range(q):
        k = rng.choice(keys)
        r = rng.random()
        if r < 0.45:
            ops.append(f"put {k} {rng.randint(-E18, E18)}")
        elif r < 0.8:
            ops.append(f"get {k}")
        elif r < 0.95:
            ops.append(f"erase {k}")
        else:
            ops.append("size")
    return fmt(ops)
