import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "Diffie–Hellman 與 ElGamal"
TOPIC = "Diffie–Hellman 金鑰交換、ElGamal 加密"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0


def manual_cases():
    return [
        ("sample", "941 627\n1\nDH 347 781"),
        ("sample2", "467 2\n3\nDH 153 197\nENC 224 197 331\nDEC 153 87 57"),
        ("big_prime", f"{2**61 - 1} 37\n3\nDH {2**60} {2**59 + 12345}\nENC 123456789 {2**61 - 3} {2**61 - 2}\nDEC {2**61 - 3} 5 6"),
    ]


def random_case(rng, size):
    hi = {"small": 1000, "medium": 10**9}.get(size, 2**62)
    q = {"small": 5, "medium": 100}.get(size, 30000)
    p = lib.random_prime(rng, 1000 if size != "small" else 11, hi)
    g = rng.randint(2, p - 2)
    out = [f"{p} {g}", str(q)]
    for _ in range(q):
        t = rng.randrange(3)
        if t == 0:
            out.append(f"DH {rng.randint(1, p - 2)} {rng.randint(1, p - 2)}")
        elif t == 1:
            out.append(f"ENC {rng.randint(1, p - 1)} {rng.randint(1, p - 2)} {rng.randint(1, p - 1)}")
        else:
            out.append(f"DEC {rng.randint(1, p - 2)} {rng.randint(1, p - 1)} {rng.randint(1, p - 1)}")
    return "\n".join(out)
