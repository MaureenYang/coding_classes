TITLE = "下一個更大的元素"
TOPIC = "單調Stack"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

N = 300000


def fmt(a):
    return f"{len(a)}\n" + " ".join(map(str, a))


def manual_cases():
    return [
        ("sample", fmt([2, 7, 3, 5, 4, 6])),
        ("n1", fmt([5])),
        ("all_equal", fmt([3, 3, 3, 3])),
        ("negative_values_and_minus1", fmt([-5, -1, -3, -1, -2, 0])),
        ("strictly_increasing", fmt(list(range(1, 11)))),
        ("strictly_decreasing", fmt(list(range(10, 0, -1)))),
        ("big_decreasing_then_max", fmt(list(range(N - 1, 0, -1)) + [10 ** 9])),
        ("big_zigzag", fmt([i if i % 2 else -i for i in range(N)])),
        ("big_all_equal", fmt([7] * N)),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 8), "medium": 1000}.get(size, N)
    v = 5 if size == "small" else 10 ** 9
    return fmt([rng.randint(-v, v) for _ in range(n)])
