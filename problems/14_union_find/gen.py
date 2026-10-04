TITLE = "併查集"
TOPIC = "Union-Find"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

N = 300000


def fmt(n, ops):
    return f"{n} {len(ops)}\n" + "\n".join(ops)


def manual_cases():
    half = N // 2
    # 每次都把「大鏈」接到新的點下面：沒有按大小合併 + 沒有路徑壓縮 → 一條長鏈
    chain = [f"union {i + 1} {i}" for i in range(1, half)] + [f"same 1 {half}"] * (N - half)
    return [
        ("sample", fmt(5, ["union 1 2", "union 3 4", "same 1 3", "union 2 4", "same 1 3", "size 4", "count"])),
        ("n1", fmt(1, ["count", "size 1", "same 1 1", "union 1 1", "count"])),
        ("self_union", fmt(3, ["union 2 2", "count", "union 1 2", "union 2 1", "union 1 1", "count", "size 2"])),
        ("no_unions", fmt(4, ["same 1 2", "count", "size 3"])),
        ("long_chain", fmt(N, chain)),
        ("star_then_query", fmt(N, [f"union 1 {i}" for i in range(2, half)] + ["count", f"size {half - 1}"] + [f"same {i} {i + 1}" for i in range(1, N - half - 1)])),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 6), "medium": 500}.get(size, N)
    q = {"small": rng.randint(1, 12), "medium": 3000}.get(size, N)
    ops = []
    for _ in range(q):
        r = rng.random()
        a, b = rng.randint(1, n), rng.randint(1, n)
        if r < 0.4:
            ops.append(f"union {a} {b}")
        elif r < 0.75:
            ops.append(f"same {a} {b}")
        elif r < 0.9:
            ops.append(f"size {a}")
        else:
            ops.append("count")
    return fmt(n, ops)
