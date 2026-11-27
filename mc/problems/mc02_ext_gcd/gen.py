from math import gcd

TITLE = "擴展歐幾里得與模反元素"
TOPIC = "擴展歐幾里得演算法"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0

BIG = 10**18


def manual_cases():
    return [
        ("sample", "6\nGCD 2024 748\nINV 3 7\nINV 6 9\nLIN 6 3 9\nLIN 6 4 9\nINV 5 1"),
        ("zeros", "5\nGCD 0 5\nGCD 7 0\nLIN 0 0 7\nLIN 0 3 7\nINV 0 13"),
        ("big_prime", f"3\nINV 123456789012345678 {BIG + 9}\nGCD {BIG} {BIG - 1}\nLIN {BIG - 2} {BIG - 4} {BIG}"),
        ("fibonacci", "2\nGCD 679891637638612258 420196140727489673\nINV 420196140727489673 679891637638612258"),
        ("powers_of_two", f"3\nGCD {2**59} {2**40 * 3}\nLIN {2**30} {2**35} {2**59}\nINV {2**59 - 1} {2**59}"),
    ]


def random_case(rng, size):
    q = {"small": 5, "medium": 100}.get(size, 100000)
    hi = {"small": 100, "medium": 10**9}.get(size, BIG)
    out = [str(q)]
    for _ in range(q):
        t = rng.randrange(3)
        m = rng.randint(1, hi)
        if t == 0:
            g = rng.choice([1, 1, rng.randint(1, 1000)])
            a, b = rng.randint(0, hi // g) * g, rng.randint(0, hi // g) * g
            if a == 0 and b == 0:
                b = g
            out.append(f"GCD {a} {b}")
        elif t == 1:
            out.append(f"INV {rng.randrange(m)} {m}")
        else:
            a = rng.randrange(m)
            if rng.random() < 0.5 and m > 1:            # 讓不互質的情況常常出現
                d = rng.choice([2, 3, 4, 6, 10, 12])
                m = max(d, m // d * d)
                a = rng.randrange(m // d) * d
            x = rng.randrange(m)
            b = a * x % m if rng.random() < 0.7 else rng.randrange(m)
            out.append(f"LIN {a} {b} {m}")
    return "\n".join(out)
