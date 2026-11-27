import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "DSA 簽章與驗證"
TOPIC = "數位簽章、DSA"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


def params(rng, qbits, pbits):
    while True:
        q = lib.random_prime(rng, 2**(qbits - 1), 2**qbits - 1)
        for _ in range(2000):
            k = rng.randint(2**(pbits - qbits - 1), 2**(pbits - qbits) - 1) * 2
            p = k * q + 1
            if p < 2**62 and lib.is_prime(p):
                while True:
                    g = pow(rng.randint(2, p - 2), (p - 1) // q, p)
                    if g != 1:
                        return p, q, g


def sign(p, q, g, s, D, e):
    S1 = pow(g, e, p) % q
    return S1, (D + s * S1) * pow(e, -1, q) % q


def manual_cases():
    p, q, g = 48731, 443, 5260
    return [
        ("sample", f"{p} {q} {g}\n4\nSIGN 242 343 427\nVERIFY 3438 343 59 166\nVERIFY 3438 344 59 166\nVERIFY 3438 343 59 165"),
        ("small_values", f"{p} {q} {g}\n3\nSIGN 1 1 1\nSIGN 442 442 442\nVERIFY {pow(g, 1, p)} 1 {sign(p, q, g, 1, 1, 1)[0]} {sign(p, q, g, 1, 1, 1)[1]}"),
    ]


def random_case(rng, size):
    qbits, pbits = {"small": (10, 20), "medium": (30, 50)}.get(size, (40, 62))
    n = {"small": 6, "medium": 200}.get(size, 20000)
    p, q, g = params(rng, qbits, pbits)
    keys = [rng.randint(1, q - 1) for _ in range(3)]
    out = [f"{p} {q} {g}", str(n)]
    for _ in range(n):
        s = rng.choice(keys)
        D = rng.randint(1, q - 1)
        while True:
            e = rng.randint(1, q - 1)
            S1, S2 = sign(p, q, g, s, D, e)
            if S1 and S2:
                break
        if rng.random() < 0.4:
            out.append(f"SIGN {s} {D} {e}")
        else:
            k = rng.random()
            if k < 0.25:
                D = D % (q - 1) + 1
            elif k < 0.4:
                S2 = S2 % (q - 1) + 1
            elif k < 0.5:
                s = rng.choice(keys)
            out.append(f"VERIFY {pow(g, s, p)} {D} {S1} {S2}")
    return "\n".join(out)
