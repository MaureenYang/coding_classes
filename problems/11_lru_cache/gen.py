TITLE = "LRU 快取"
TOPIC = "List+Hash"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

Q = 300000


def fmt(c, ops):
    return f"{c} {len(ops)}\n" + "\n".join(ops)


def manual_cases():
    return [
        ("sample", fmt(2, ["put 1 1", "put 2 2", "get 1", "put 3 3", "get 2", "put 4 4", "get 1"])),
        ("capacity_1", fmt(1, ["put 1 1", "get 1", "put 2 2", "get 1", "get 2", "put 2 5", "get 2", "put 3 3"])),
        ("update_existing_no_evict", fmt(2, ["put 1 1", "put 2 2", "put 1 10", "put 3 3", "get 1", "get 2", "get 3"])),
        ("get_changes_order", fmt(3, ["put 1 1", "put 2 2", "put 3 3", "get 1", "get 2", "put 4 4", "get 3", "put 5 5"])),
        ("get_missing", fmt(3, ["get 0", "get 1000000000", "put 0 0", "get 0"])),
        ("big_cycle_evict_every_time", fmt(100000, [f"put {i % 100001} {i}" for i in range(Q)])),
        ("big_hot_key", fmt(1000, [op for i in range(Q // 2) for op in ("get 7", f"put {i} {i}")])),
    ]


def random_case(rng, size):
    c = {"small": rng.randint(1, 3), "medium": rng.randint(1, 50)}.get(size, rng.randint(1, 100000))
    q = {"small": rng.randint(1, 15), "medium": 3000}.get(size, Q)
    keyspace = max(2, int(c * rng.uniform(1.0, 3.0)))
    ops = []
    for _ in range(q):
        k = rng.randint(0, keyspace)
        if rng.random() < 0.5:
            ops.append(f"get {k}")
        else:
            ops.append(f"put {k} {rng.randint(0, 10 ** 9)}")
    return fmt(c, ops)
