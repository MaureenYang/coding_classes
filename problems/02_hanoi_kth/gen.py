TITLE = "河內塔的第 k 步"
TOPIC = "遞迴/分治"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(qs):
    return f"{len(qs)}\n" + "\n".join(f"{n} {k}" for n, k in qs)


def manual_cases():
    every_step_small = [(n, k) for n in range(1, 6) for k in range(1, 2 ** n)]
    return [
        ("sample", fmt([(2, 1), (2, 2), (3, 4)])),
        ("n1", fmt([(1, 1)])),
        ("all_steps_n_le_5", fmt(every_step_small)),
        ("n60_first_middle_last", fmt([(60, 1), (60, 2 ** 59), (60, 2 ** 60 - 1), (60, 2 ** 59 - 1), (60, 2 ** 59 + 1)])),
        ("powers_of_two_k", fmt([(60, 2 ** i) for i in range(60)])),
        ("last_step_every_n", fmt([(n, 2 ** n - 1) for n in range(1, 61)])),
    ]


def random_case(rng, size):
    t = {"small": 5, "medium": 1000}.get(size, 100000)
    maxn = 8 if size == "small" else 60
    qs = []
    for _ in range(t):
        n = rng.randint(1, maxn)
        qs.append((n, rng.randint(1, 2 ** n - 1)))
    return fmt(qs)
