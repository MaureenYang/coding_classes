TITLE = "環狀佇列"
TOPIC = "Queue"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(k, ops):
    return f"{k} {len(ops)}\n" + "\n".join(ops)


def manual_cases():
    wrap = []
    for i in range(10):  # 反覆繞圈
        wrap += [f"enqueue {i}", f"enqueue {i + 100}", "rear", "dequeue", "front", "dequeue", "size"]
    return [
        ("sample", fmt(3, ["enqueue 1", "enqueue 2", "enqueue 3", "enqueue 4", "rear", "dequeue",
                           "enqueue 4", "rear", "front"])),
        ("empty_ops", fmt(2, ["dequeue", "front", "rear", "size", "enqueue 1", "dequeue", "dequeue", "rear"])),
        ("k1", fmt(1, ["enqueue 5", "enqueue 6", "front", "rear", "dequeue", "enqueue 7", "rear", "size", "dequeue", "dequeue"])),
        ("wrap_around_k3", fmt(3, wrap)),
        ("fill_drain_fill", fmt(4, [f"enqueue {i}" for i in range(6)] + ["dequeue"] * 5 + [f"enqueue {i}" for i in range(6)] + ["front", "rear", "size"])),
        ("big_k_full", fmt(100000, [f"enqueue {i}" for i in range(100001)] + ["front", "rear", "size"] + ["dequeue"] * 100 + ["rear"])),
    ]


def random_case(rng, size):
    k = {"small": rng.randint(1, 4), "medium": rng.randint(1, 50)}.get(size, rng.randint(1, 100000))
    q = {"small": rng.randint(1, 20), "medium": 3000}.get(size, 300000)
    p = rng.uniform(0.35, 0.65)  # enqueue 比例，控制佇列常常滿 / 常常空
    ops = []
    for _ in range(q):
        r = rng.random()
        if r < p:
            ops.append(f"enqueue {rng.randint(-10 ** 9, 10 ** 9)}")
        elif r < 0.9:
            ops.append("dequeue")
        else:
            ops.append(rng.choice(["front", "rear", "size"]))
    return fmt(k, ops)
