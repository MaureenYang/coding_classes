import importlib.util, os

_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py")
_s = importlib.util.spec_from_file_location("_mrlib", _p)
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "元素的階與原根"
TOPIC = "元素的階、原根"
DIFFICULTY = "★★★"
TIME_LIMIT = 2.0


def manual_cases():
    return [
        ("sample", "4\n11 3\n11 2\n13 12\n2 1"),
        ("book_examples", "3\n7 2\n7 3\n29 2"),
        ("one_has_order_one", "2\n1000003 1\n999999999989 1"),
        ("minus_one", "2\n1000000007 1000000006\n999999999989 999999999988"),
        ("big_primes", "3\n999999999989 2\n999999000001 7\n1000000000039 5"),
        ("primorial_plus_one", "1\n200560490131 3"),
        ("safe_prime", "2\n999999999959 4\n999999999959 999999999958"),
        ("fermat_prime", "2\n65537 2\n65537 3"),
    ]


def random_case(rng, size):
    t = {"small": 5, "medium": 10}.get(size, 20)
    hi = {"small": 100, "medium": 10**6}.get(size, 10**12)
    out = [str(t)]
    for _ in range(t):
        p = lib.random_prime(rng, 3, hi)
        out.append(f"{p} {rng.randint(1, p - 1)}")
    return "\n".join(out)
