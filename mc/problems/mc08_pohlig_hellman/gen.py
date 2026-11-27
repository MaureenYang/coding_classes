import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "Pohlig–Hellman"
TOPIC = "Pohlig–Hellman 演算法、離散對數"
DIFFICULTY = "★★★★"
TIME_LIMIT = 2.0

SMALL_PRIMES = [q for q in range(2, 100000) if lib.is_prime(q)]


def smooth_prime(rng, bound, limit):
    """回傳 (p, 原根)，p − 1 的質因數都 ≤ bound，p ≤ limit"""
    cands = [q for q in SMALL_PRIMES if q <= bound]
    while True:
        n, fs = 2, {2}
        while True:
            q = rng.choice(cands)
            if n * q > limit:
                break
            n *= q
            fs.add(q)
        if n * 2 < limit // 1000 and limit > 10**6:
            continue
        p = n + 1
        if lib.is_prime(p):
            g = next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in fs))
            return p, g


def manual_cases():
    return [
        ("sample", "2\n11251 23 9689\n11251 23 1"),
        ("h_equals_g", "1\n11251 23 23"),
        ("power_of_two_order", f"2\n65537 3 {pow(3, 12345, 65537)}\n65537 3 65536"),
        ("big_smooth", "2\n200560490131 34 " + str(pow(34, 123456789123, 200560490131)) + "\n200560490131 34 3"),
    ]


def random_case(rng, size):
    t = {"small": 3, "medium": 5}.get(size, 10)
    bound = {"small": 30, "medium": 1000}.get(size, 100000)
    limit = {"small": 10**6, "medium": 10**12}.get(size, 10**18)
    out = [str(t)]
    for _ in range(t):
        p, g = smooth_prime(rng, bound, limit)
        out.append(f"{p} {g} {rng.randint(1, p - 1)}")
    return "\n".join(out)
