import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "橢圓曲線運算"
TOPIC = "橢圓曲線加法、倍點運算"
DIFFICULTY = "★★★"
TIME_LIMIT = 2.0


def add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def mul(k, P, A, p):
    R = None
    while k:
        if k & 1:
            R = add(R, P, A, p)
        P, k = add(P, P, A, p), k >> 1
    return R


def random_point(rng, p, A, B):
    """p ≡ 3 (mod 4)：平方根是 rhs^((p+1)/4)"""
    while True:
        x = rng.randrange(p)
        r = (x ** 3 + A * x + B) % p
        y = pow(r, (p + 1) // 4, p)
        if y * y % p == r:
            return (x, y if rng.random() < 0.5 else (p - y) % p)


def pt(P):
    return "O" if P is None else f"{P[0]} {P[1]}"


def manual_cases():
    return [
        ("sample", "13 3 8\n5\nADD 9 7 1 8\nADD 9 7 9 7\nADD 9 7 9 6\nMUL 0 9 7\nADD O 1 8"),
        ("book_ecdh", "3851 324 1287\n3\nMUL 1194 920 303\nMUL 1759 920 303\nMUL 1194 3684 3125"),
        ("inverse_points", "13 3 8\n2\nMUL 2 12 2\nADD 12 2 12 11"),
        ("y_zero", "11 1 0\n3\nADD 0 0 0 0\nMUL 3 0 0\nADD O O"),
        ("big_prime", f"{2**61 - 1} 3 7\n1\nMUL {2**63 - 1} O"),
    ]


def random_case(rng, size):
    hi = {"small": 100, "medium": 10**9}.get(size, 2**62)
    q = {"small": 6, "medium": 300}.get(size, 2000)
    while True:
        p = lib.random_prime(rng, 7, hi)
        if p % 4 == 3:
            break
    while True:
        A, B = rng.randrange(p), rng.randrange(p)
        if (4 * A ** 3 + 27 * B * B) % p:
            break
    pts = [random_point(rng, p, A, B) for _ in range(8)]
    out = [f"{p} {A} {B}", str(q)]
    for _ in range(q):
        P = rng.choice(pts)
        k = rng.random()
        if k < 0.35:
            Q = rng.choice([rng.choice(pts), P, (P[0], (p - P[1]) % p), None])
            out.append(f"ADD {pt(P)} {pt(Q)}")
        else:
            out.append(f"MUL {rng.randint(0, 2**63 - 1) if size != 'small' else rng.randint(0, 50)} {pt(P)}")
        if rng.random() < 0.1:                       # 讓更多點參與
            pts.append(mul(rng.randint(1, 1000), P, A, p) or P)
    return "\n".join(out)
