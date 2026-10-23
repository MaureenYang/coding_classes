TITLE = "動態二維矩陣"
TOPIC = "指標的指標"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


def mat(rng, r, c, lim):
    return [[rng.randint(-lim, lim) for _ in range(c)] for _ in range(r)]


def fmt(a, b):
    def one(m):
        return f"{len(m)} {len(m[0])}\n" + "".join(" ".join(map(str, row)) + "\n" for row in m)
    return one(a) + one(b)


def manual_cases():
    import random
    rng = random.Random(1)
    return [
        ("sample", fmt([[1, 2, 3], [4, 5, 6]], [[1, 0], [0, 1], [1, 1]])),
        ("one_by_one", fmt([[7]], [[-3]])),
        ("same_square_shape", fmt([[1, 2], [3, 4]], [[5, 6], [7, 8]])),
        ("row_times_col", fmt([[1, 2, 3, 4]], [[1], [2], [3], [4]])),
        ("col_times_row", fmt([[1], [2], [3]], [[4, 5, 6]])),
        ("cannot_either", fmt([[1, 2, 3]], [[1, 2]])),
        ("same_shape_not_square", fmt([[1, 2, 3], [4, 5, 6]], [[6, 5, 4], [3, 2, 1]])),
        ("extreme_values_max_size", fmt([[1000] * 200 for _ in range(200)], [[-1000] * 200 for _ in range(200)])),
        ("tall_thin", fmt(mat(rng, 200, 1, 1000), mat(rng, 1, 200, 1000))),
    ]


def random_case(rng, size):
    hi = {"small": 3, "medium": 30}.get(size, 200)
    r1, c1 = rng.randint(1, hi), rng.randint(1, hi)
    k = rng.random()
    if k < 0.4:
        r2, c2 = c1, rng.randint(1, hi)          # 可以相乘
    elif k < 0.7:
        r2, c2 = r1, c1                          # 可以相加（方陣時也能相乘）
    else:
        r2, c2 = rng.randint(1, hi), rng.randint(1, hi)
    lim = {"small": 5}.get(size, 1000)
    return fmt(mat(rng, r1, c1, lim), mat(rng, r2, c2, lim))
