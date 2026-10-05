TITLE = "用指標做矩陣"
TOPIC = "指標"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0
RANDOM_PLAN = [("small", 5), ("medium", 3), ("large", 2)]


def mat(rng, r, c, v):
    return [[rng.randint(-v, v) for _ in range(c)] for _ in range(r)]


def fmt(A, B):
    def m(M):
        return f"{len(M)} {len(M[0])}\n" + "\n".join(" ".join(map(str, row)) for row in M)
    return m(A) + "\n" + m(B)


def manual_cases():
    import random
    rng = random.Random(5)
    big = [[10000] * 200 for _ in range(200)]
    neg = [[-10000] * 200 for _ in range(200)]
    return [
        ("sample", fmt([[1, 2, 3], [4, 5, 6]], [[1, 0], [0, 1], [1, 1]])),
        ("one_by_one", fmt([[7]], [[-3]])),
        ("row_times_column", fmt([[1, 2, 3, 4]], [[1], [2], [3], [4]])),
        ("column_times_row", fmt([[1], [2], [3]], [[4, 5, 6]])),
        ("both_mismatch", fmt([[1, 2]], [[1, 2, 3]])),
        ("square_same_size", fmt(mat(rng, 3, 3, 9), mat(rng, 3, 3, 9))),
        ("max_values_long_long", fmt(big, neg)),
    ]


def random_case(rng, size):
    n = {"small": 4, "medium": 30}.get(size, 200)
    r1, c1 = rng.randint(1, n), rng.randint(1, n)
    kind = rng.random()
    if kind < 0.4:
        r2, c2 = c1, rng.randint(1, n)           # 可以相乘
    elif kind < 0.7:
        r2, c2 = r1, c1                          # 可以相加
        if r1 == c1:
            pass
    else:
        r2, c2 = rng.randint(1, n), rng.randint(1, n)
    v = 9 if size == "small" else 10 ** 4
    return fmt(mat(rng, r1, c1, v), mat(rng, r2, c2, v))
