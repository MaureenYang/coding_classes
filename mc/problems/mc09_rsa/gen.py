import importlib.util, os
from math import gcd

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "RSA 加解密"
TOPIC = "RSA 公鑰密碼、RSA 簽章"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0


def manual_cases():
    return [
        ("sample", "5\nKEY 1223 1987 948047\nENC 2430101 948047 1070777\nDEC 1223 1987 948047 1473513\n"
                   "KEY 11 13 3\nVERIFY 2430101 948047 1070777 153337"),
        ("verify_fail", "2\nVERIFY 2430101 948047 1070778 153337\nVERIFY 2430101 948047 1070777 153338"),
        ("small_key", "4\nKEY 3 5 3\nENC 15 3 0\nENC 15 3 14\nDEC 3 5 3 9"),
        ("big_primes", "3\nKEY 2147483647 2147483629 65537\nENC 4611685975477714963 65537 4611685975477714962\n"
                       "DEC 2147483647 2147483629 65537 1"),
        ("e_not_coprime", "2\nKEY 7 13 9\nKEY 101 103 17"),
    ]


def random_case(rng, size):
    q = {"small": 5, "medium": 200}.get(size, 30000)
    hi = {"small": 100, "medium": 10**6}.get(size, 2**31 - 1)
    out = [str(q)]
    for _ in range(q):
        p1 = lib.random_prime(rng, 3, hi)
        p2 = lib.random_prime(rng, 3, hi)
        while p2 == p1:
            p2 = lib.random_prime(rng, 3, hi)
        N, phi = p1 * p2, (p1 - 1) * (p2 - 1)
        e = rng.choice([3, 17, 65537, rng.randrange(3, phi, 2)])
        if rng.random() < 0.85:
            while gcd(e, phi) != 1:
                e = rng.randrange(3, phi, 2)
        t = rng.randrange(4)
        if t == 0 or gcd(e, phi) != 1:
            out.append(f"KEY {p1} {p2} {e}")
        elif t == 1:
            out.append(f"ENC {N} {e} {rng.randrange(N)}")
        elif t == 2:
            out.append(f"DEC {p1} {p2} {e} {rng.randrange(N)}")
        else:
            D = rng.randrange(N)
            S = pow(D, pow(e, -1, phi), N)
            if rng.random() < 0.4:
                S = (S + rng.randint(1, N - 1)) % N
            out.append(f"VERIFY {N} {e} {D} {S}")
    return "\n".join(out)
