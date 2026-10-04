TITLE = "滑動視窗最大值"
TOPIC = "Deque"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

N = 10 ** 6


def fmt(k, a):
    return f"{len(a)} {k}\n" + " ".join(map(str, a))


def manual_cases():
    return [
        ("sample", fmt(3, [1, 3, -1, -3, 5, 3, 6, 7])),
        ("n1_k1", fmt(1, [-7])),
        ("k1", fmt(1, [4, -2, 9, 9, 0])),
        ("k_equals_n", fmt(6, [5, 1, 9, -3, 9, 2])),
        ("all_negative", fmt(2, [-10 ** 9, -5, -10 ** 9, -10 ** 9])),
        ("increasing", fmt(3, list(range(10)))),
        ("decreasing", fmt(3, list(range(10, 0, -1)))),
        ("big_decreasing_k_half", fmt(N // 2, list(range(N, 0, -1)))),
        ("big_increasing_k2", fmt(2, list(range(N)))),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 10), "medium": 2000}.get(size, N)
    k = rng.randint(1, n) if rng.random() < 0.7 else rng.choice([1, n, min(n, 2)])
    v = 5 if size == "small" else 10 ** 9
    return fmt(k, [rng.randint(-v, v) for _ in range(n)])
