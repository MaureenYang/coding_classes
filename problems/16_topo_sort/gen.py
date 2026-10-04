TITLE = "拓撲排序"
TOPIC = "Graph/Topo"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

N = 200000


def fmt(n, edges):
    return f"{n} {len(edges)}\n" + "\n".join(f"{a} {b}" for a, b in edges)


def random_dag(rng, n, m):
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    if n >= 2:
        for _ in range(m):
            i, j = sorted(rng.sample(range(n), 2))
            edges.append((perm[i], perm[j]))
    return edges


def manual_cases():
    return [
        ("sample", fmt(5, [(3, 1), (1, 2), (3, 2), (5, 4)])),
        ("n1_no_edges", fmt(1, [])),
        ("no_edges", fmt(6, [])),
        ("self_loop", fmt(3, [(1, 2), (2, 2)])),
        ("two_cycle", fmt(2, [(1, 2), (2, 1)])),
        ("cycle_not_reachable_from_start", fmt(5, [(1, 2), (3, 4), (4, 5), (5, 3)])),
        ("duplicate_edges", fmt(3, [(2, 1), (2, 1), (2, 1), (3, 1)])),
        ("reverse_chain", fmt(6, [(i + 1, i) for i in range(1, 6)])),
        ("big_chain", fmt(N, [(i, i + 1) for i in range(1, N)])),
        ("big_reverse_chain_with_cycle", fmt(N, [(i + 1, i) for i in range(1, N)] + [(1, N)])),
        ("big_star", fmt(N, [(N, i) for i in range(1, N)])),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 6), "medium": 300}.get(size, N)
    m = {"small": rng.randint(0, 8), "medium": 600}.get(size, N)
    edges = random_dag(rng, n, m)
    if n >= 2 and rng.random() < 0.3:  # 30% 加一條反向邊，可能造成環
        a, b = rng.sample(range(1, n + 1), 2)
        edges.append((a, b))
    rng.shuffle(edges)
    return fmt(n, edges)
