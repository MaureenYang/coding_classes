TITLE = "二維格基約化"
TOPIC = "Gauss 格基約化、最短向量"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

LIM = 10**9


def fmt(tests):
    return "\n".join([str(len(tests))] + [" ".join(map(str, a + b)) for a, b in tests])


def bad_basis(rng, lim, coef):
    """從一組隨機的短基底出發，乘上行列式 ±1 的整數矩陣，得到一組「壞」基底"""
    while True:
        a = (rng.randint(-lim, lim), rng.randint(-lim, lim))
        b = (rng.randint(-lim, lim), rng.randint(-lim, lim))
        if a[0] * b[1] - a[1] * b[0] != 0:
            break
    for _ in range(rng.randint(1, 6)):
        k = rng.randint(-coef, coef)
        if rng.random() < 0.5:
            a, b = b, a
        nb = (b[0] + k * a[0], b[1] + k * a[1])
        if max(abs(x) for x in nb) <= LIM:
            b = nb
    return a, b


def manual_cases():
    return [
        ("sample", fmt([((66586820, 65354729), (6513996, 6393464)), ((1, 0), (0, 1)), ((3, 1), (5, 2))])),
        ("already_reduced", fmt([((2, 0), (1, 3)), ((5, 0), (0, 5)), ((1, 0), (-1, 1))])),
        ("half_ties", fmt([((2, 0), (1, 5)), ((2, 0), (-1, 5)), ((2, 0), (3, 1)), ((4, 0), (-6, 1)), ((1, 1), (2, 1))])),
        ("equal_norms", fmt([((3, 4), (5, 0)), ((5, 0), (3, 4)), ((0, 5), (4, -3))])),
        ("huge", fmt([((LIM, LIM - 1), (LIM - 1, LIM - 2)), ((-LIM, LIM), (LIM, -LIM + 1)), ((LIM, 1), (1, 0))])),
    ]


def random_case(rng, size):
    t = {"small": 5, "medium": 100}.get(size, 100000)
    lim = {"small": 10, "medium": 1000}.get(size, 30000)
    coef = {"small": 5, "medium": 1000}.get(size, 30000)
    return fmt([bad_basis(rng, lim, coef) for _ in range(t)])
