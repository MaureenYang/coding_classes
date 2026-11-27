import importlib.util, os

_s = importlib.util.spec_from_file_location("_mrlib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_mrlib.py"))
lib = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lib)

TITLE = "Miller–Rabin 質數檢定"
TOPIC = "Miller–Rabin 質數檢定"
DIFFICULTY = "★★★"
TIME_LIMIT = 2.0

# 卡邁克爾數、對多個底數的強偽質數：只用費馬檢定或只用少數底數會判錯
TRICKY = [561, 1105, 1729, 2465, 2821, 6601, 8911, 2047, 1373653, 25326001, 3215031751,
          2152302898747, 3474749660383, 341550071728321, 3825123056546413051,
          9223372036854775783, 9223372036854775807, 2305843009213693951, 4611686014132420609,
          999999999999999989, 1000000000000000003, 3037000493 * 3037000453]


def manual_cases():
    return [
        ("sample", "6\n2\n9\n561\n97\n1373653\n1000000007"),
        ("tiny", "\n".join(["11"] + [str(n) for n in range(2, 13)])),
        ("tricky", "\n".join([str(len(TRICKY))] + [str(n) for n in TRICKY])),
    ]


def random_case(rng, size):
    t = {"small": 10, "medium": 1000}.get(size, 10000)
    bits = {"small": 12, "medium": 40}.get(size, 63)
    out = [str(t)]
    for _ in range(t):
        k = rng.random()
        if k < 0.3:
            n = lib.random_prime(rng, 2, 2**bits - 1)
        elif k < 0.5 and bits > 20:          # 兩個大質數的乘積
            a = lib.random_prime(rng, 3, 2**(bits // 2) - 1)
            n = a * lib.random_prime(rng, 3, (2**bits - 1) // a)
        else:
            n = rng.randint(2, 2**bits - 1)
        out.append(str(n))
    return "\n".join(out)
