import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "整數分解"
TOPIC = "Pollard ρ、Miller–Rabin"
DIFFICULTY = "★★★★"
TIME_LIMIT = 2.0


def manual_cases():
    return [
        ("sample", "5\n12\n97\n13927189\n1000000016000000063\n1024"),
        ("tiny", "6\n2\n3\n4\n6\n8\n30"),
        ("hard_semiprimes", "4\n" + "\n".join(str(x) for x in [3037000493 * 3037000453, 2147483647 * 2147483629,
                                                               4611686014132420609, 999999999999999989])),
        ("carmichael_and_spsp", "4\n561\n3825123056546413051\n341550071728321\n9223372036854775807"),
        ("prime_powers", f"3\n{3**39}\n{2**62}\n{1000003**3}"),
    ]


def random_case(rng, size):
    t = {"small": 10, "medium": 50}.get(size, 100)
    bits = {"small": 20, "medium": 48}.get(size, 63)
    out = [str(t)]
    for _ in range(t):
        k = rng.random()
        if k < 0.4 and bits > 30:
            a = lib.random_prime(rng, 2**(bits // 2 - 4), 2**(bits // 2) - 1)
            n = a * lib.random_prime(rng, 3, (2**bits - 1) // a)
        else:
            n = rng.randint(2, 2**bits - 1)
        out.append(str(n))
    return "\n".join(out)
