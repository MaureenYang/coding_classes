TITLE = "快速冪"
TOPIC = "平方乘法、128 位元乘法"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0

M63 = 2**63 - 1


def manual_cases():
    return [
        ("sample", "4\n3 218 1000\n2 10 1000\n5 0 7\n123 456 1"),
        ("fermat", "3\n2 1000000006 1000000007\n7 998244352 998244353\n17 1000000000000000002 1000000000000000003"),
        ("zero_base", "3\n0 0 5\n0 5 5\n0 1 1"),
        ("max_values", f"3\n{M63} {M63} {M63}\n{M63 - 1} {M63} {M63 - 24}\n{10**18} {10**18} {10**18 + 9}"),
    ]


def random_case(rng, size):
    q = {"small": 5, "medium": 1000}.get(size, 100000)
    bits = {"small": 10}.get(size, 63)
    out = [str(q)]
    for _ in range(q):
        m = rng.randint(1, 2**bits - 1)
        out.append(f"{rng.randint(0, 2**bits - 1)} {rng.randint(0, 2**bits - 1)} {m}")
    return "\n".join(out)
