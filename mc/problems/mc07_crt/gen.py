from math import gcd

TITLE = "中國剩餘定理"
TOPIC = "中國剩餘定理"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0


def fmt(tests):
    out = [str(len(tests))]
    for pairs in tests:
        out.append(str(len(pairs)))
        out += [f"{a} {m}" for a, m in pairs]
    return "\n".join(out)


def coprime_moduli(rng, k, limit):
    ms, prod = [], 1
    tries = 0
    while len(ms) < k and tries < 10000:
        tries += 1
        cap = limit // prod
        if cap < 2:
            break
        m = rng.randint(2, min(cap, max(2, int(limit ** (1 / k) * 2))))
        if all(gcd(m, x) == 1 for x in ms):
            ms.append(m)
            prod *= m
    return ms


def manual_cases():
    return [
        ("sample", fmt([[(2, 3), (3, 7)], [(2, 3), (3, 7), (4, 16)], [(5, 8)]])),
        ("book_example", fmt([[(1, 5), (9, 11)], [(0, 2), (0, 3), (1, 5)]])),
        ("modulus_one", fmt([[(0, 1), (3, 4)]])),
        ("max_product", fmt([[(999999999999999988, 999999999999999989), (1, 2)],
                             [(123456788, 1000000007), (987654320, 998244353)]])),
        ("many_small_primes", fmt([[(i, p) for i, p in enumerate([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])]])),
    ]


def random_case(rng, size):
    t = {"small": 3, "medium": 100}.get(size, 10000)
    limit = {"small": 1000, "medium": 10**12}.get(size, 10**18)
    tests = []
    for _ in range(t):
        ms = coprime_moduli(rng, rng.randint(1, 8), limit)
        if not ms:
            ms = [rng.randint(2, 100)]
        tests.append([(rng.randrange(m), m) for m in ms])
    return fmt(tests)
