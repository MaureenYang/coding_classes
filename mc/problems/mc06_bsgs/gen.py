import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "嬰兒步巨人步"
TOPIC = "離散對數、Shanks 嬰兒步巨人步演算法"
DIFFICULTY = "★★★"
TIME_LIMIT = 2.0


def manual_cases():
    return [
        ("sample", "4\n17389 9704 13896\n11 2 1\n11 3 2\n11 3 9"),
        ("h_is_g", "2\n999999999989 2 2\n1000003 5 5"),
        ("order_two", "2\n1000003 1000002 1\n1000003 1000002 1000002"),
        ("g_is_one", "2\n101 1 1\n101 1 5"),
        ("big_answer", "2\n999999999989 2 " + str(pow(2, 999999999987, 999999999989)) +
         "\n999999999959 7 " + str(pow(7, 123456789012, 999999999959))),
        ("max_safe_prime", "3\n999999999959 4 3\n999999999959 4 " + str(pow(4, 499999999977, 999999999959)) +
         "\n999999999959 13 1"),
    ]


def random_case(rng, size):
    t = {"small": 5, "medium": 10}.get(size, 10)
    hi = {"small": 200, "medium": 10**8}.get(size, 10**12)
    out = [str(t)]
    for _ in range(t):
        p = lib.random_prime(rng, 5, hi)
        g = rng.randint(2, p - 1)
        h = pow(g, rng.randrange(p - 1), p) if rng.random() < 0.8 else rng.randint(1, p - 1)
        out.append(f"{p} {g} {h}")
    return "\n".join(out)
