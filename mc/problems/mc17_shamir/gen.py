import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "Shamir 秘密分享"
TOPIC = "門檻秘密分享、Lagrange 內插"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


def f(coeffs, x, p):
    return sum(c * pow(x, k, p) for k, c in enumerate(coeffs)) % p


def manual_cases():
    return [
        ("sample", "101\n3\nSHARE 11 2 3 34\nRECOVER 2 1 45 3 12\nRECOVER 3 1 45 2 79 3 12"),
        ("threshold_one", "101\n2\nSHARE 42 1 4\nRECOVER 1 7 42"),
        ("big_prime", f"{2**61 - 1}\n2\nSHARE 31415926535 3 5 {2**61 - 2} 12345\nRECOVER 2 1 5 2 7"),
        ("large_x", f"1000000007\n1\nRECOVER 3 1000000006 1 999999999 2 123456789 3"),
    ]


def random_case(rng, size):
    p = lib.random_prime(rng, 50, {"small": 1000, "medium": 10**9}.get(size, 2**62 - 1))
    n_q = {"small": 4, "medium": 50}.get(size, 200)
    tmax = {"small": 4, "medium": 20}.get(size, 100)
    out = [str(p), str(n_q)]
    for _ in range(n_q):
        t = rng.randint(1, min(tmax, p - 1))
        n = rng.randint(t, min(tmax, p - 1))
        coeffs = [rng.randrange(p) for _ in range(t)]
        if rng.random() < 0.5:
            out.append("SHARE " + " ".join(map(str, [coeffs[0], t, n] + coeffs[1:])))
        else:
            k = rng.randint(1, t) if rng.random() < 0.2 else t
            xs = rng.sample(range(1, min(p, 10**6)), k)
            out.append("RECOVER " + str(k) + " " + " ".join(f"{x} {f(coeffs, x, p)}" for x in xs))
    return "\n".join(out)
