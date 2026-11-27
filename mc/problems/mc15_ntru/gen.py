TITLE = "NTRU 加解密"
TOPIC = "NTRU 公鑰密碼、卷積多項式環"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


# ---- (Z/pZ)[x]/(x^N − 1) 中的反元素（p 是質數），同第 23 課 ----
def trim(a):
    while a and a[-1] == 0:
        a = a[:-1]
    return a


def pdivmod(a, b, p):
    a, b = trim([x % p for x in a]), trim([x % p for x in b])
    q = [0] * max(len(a) - len(b) + 1, 1)
    inv = pow(b[-1], -1, p)
    r = a[:]
    while r and len(r) >= len(b):
        s, c = len(r) - len(b), r[-1] * inv % p
        q[s] = c
        for i, bc in enumerate(b):
            r[i + s] = (r[i + s] - c * bc) % p
        r = trim(r)
    return trim(q), r


def pmul(a, b, p):
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                c[i + j] = (c[i + j] + x * y) % p
    return trim(c)


def psub(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])


def inverse_mod(a, N, p):
    m = [-1] + [0] * (N - 1) + [1]
    r0, r1 = trim([x % p for x in m]), trim([x % p for x in a])
    s0, s1 = [], [1]
    while r1:
        q, r = pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
    if len(r0) != 1:
        return None
    c = pow(r0[0], -1, p)
    s = [x * c % p for x in s0]
    return s + [0] * (N - len(s))


def conv(a, b, N, q):
    c = [0] * N
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                c[(i + j) % N] += ai * bj
    return [x % q for x in c]


def ternary(rng, N, d1, d2):
    a = [1] * d1 + [-1] * d2 + [0] * (N - d1 - d2)
    rng.shuffle(a)
    return a


def keypair(rng, N, p, q, d):
    while True:
        f = ternary(rng, N, d + 1, d)
        Fq, Fp = inverse_mod(f, N, q), inverse_mod(f, N, p)
        if Fq and Fp:
            return f, Fp, Fq, ternary(rng, N, d, d)


def poly(a):
    return " ".join(map(str, a))


def manual_cases():
    f = [-1, 0, 1, 1, -1, 0, 1]
    g = [0, -1, -1, 0, 1, 0, 1]
    Fq, Fp = inverse_mod(f, 7, 41), inverse_mod(f, 7, 3)
    h = conv(Fq, g, 7, 41)
    m, r = [1, -1, 1, 1, 0, -1, 0], [-1, 1, 0, 0, 0, -1, 1]
    e = [(3 * x + y) % 41 for x, y in zip(conv(h, r, 7, 41), m)]
    return [
        ("sample", "7 3 41\n3\n" + f"KEY {poly(Fq)} {poly(g)}\nENC {poly(h)} {poly(r)} {poly(m)}\nDEC {poly(f)} {poly(Fp)} {poly(e)}"),
    ]


def random_case(rng, size):
    N, q, d = {"small": (11, 47, 2), "medium": (107, 683, 30)}.get(size, (251, 65521, 80))
    p = 3
    qn = {"small": 6, "medium": 30}.get(size, 60)
    out = [f"{N} {p} {q}", str(qn)]
    keys = [keypair(rng, N, p, q, d) for _ in range(2)]
    for _ in range(qn):
        f, Fp, Fq, g = rng.choice(keys)
        h = conv(Fq, g, N, q)
        t = rng.randrange(3)
        if t == 0:
            out.append(f"KEY {poly(Fq)} {poly(g)}")
        else:
            m = [rng.choice([-1, 0, 1]) for _ in range(N)]
            r = ternary(rng, N, d, d)
            if t == 1:
                out.append(f"ENC {poly(h)} {poly(r)} {poly(m)}")
            else:
                e = [(p * x + y) % q for x, y in zip(conv(h, r, N, q), m)]
                out.append(f"DEC {poly(f)} {poly(Fp)} {poly(e)}")
    return "\n".join(out)
