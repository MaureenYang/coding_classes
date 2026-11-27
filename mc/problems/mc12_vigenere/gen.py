import os

TITLE = "破解 Vigenère 密碼"
TOPIC = "Vigenère 密碼、重合指數、卡方統計量"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

FREQ = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
        6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074]
MAXL = 15

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_english.txt"), encoding="utf-8") as f:
    LETTERS = "".join(c for c in f.read().upper() if c.isalpha())
LOOP = LETTERS * 3


def encrypt(plain, key):
    return "".join(chr((ord(c) + ord(key[i % len(key)]) - 130) % 26 + 65) for i, c in enumerate(plain))


def ioc(col):
    n = len(col)
    return sum(col.count(chr(65 + i)) * (col.count(chr(65 + i)) - 1) for i in range(26)) / (n * (n - 1))


def avg_ioc(ct, L):
    return sum(ioc(ct[i::L]) for i in range(L)) / L


def chi(col, s):
    cnt = [0] * 26
    for c in col:
        cnt[(ord(c) - 65 - s) % 26] += 1
    n = len(col)
    return sum((cnt[i] - n * FREQ[i] / 100) ** 2 / (n * FREQ[i] / 100) for i in range(26))


def ok(plain, key):
    """題目描述的方法要能「明確地」找出正確答案（各項都留有安全距離，避免浮點誤差）"""
    ct, L = encrypt(plain, key), len(key)
    if any(avg_ioc(ct, l) >= 0.057 for l in range(1, L)) or avg_ioc(ct, L) < 0.063:
        return False
    for i in range(L):
        sc = sorted((chi(ct[i::L], s), s) for s in range(26))
        if sc[0][1] != ord(key[i]) - 65 or sc[0][0] > 0.75 * sc[1][0]:
            return False
    return True


def make(rng, L, letters):
    for _ in range(1000):
        key = "".join(chr(65 + rng.randrange(26)) for _ in range(L))
        if any(L % d == 0 and key == key[:d] * (L // d) for d in range(1, L)):
            continue                                      # 金鑰不能是更短字串的重複
        i = rng.randrange(len(LETTERS))
        plain = LOOP[i:i + letters]
        if ok(plain, key):
            return encrypt(plain, key)
    raise RuntimeError("找不到合適的測資")


def manual_cases():
    import random
    rng = random.Random(7)
    sample_plain = LETTERS[:300]
    assert ok(sample_plain, "CRYPTO")
    return [
        ("sample", "1\n" + encrypt(sample_plain, "CRYPTO")),
        ("key_length_one", "1\n" + make(rng, 1, 120)),
        ("key_length_fifteen", "1\n" + make(rng, 15, 2500)),
        ("prime_lengths", "3\n" + "\n".join(make(rng, L, 60 * L) for L in (7, 11, 13))),
        ("long_text", "1\n" + make(rng, 9, 4000)),
    ]


def random_case(rng, size):
    t = {"small": 2, "medium": 5}.get(size, 10)
    out = [str(t)]
    for _ in range(t):
        L = rng.randint(1, {"small": 4, "medium": 8}.get(size, 15))
        out.append(make(rng, L, rng.randint(60 * L, max(60 * L, {"small": 400}.get(size, 4000)))))
    return "\n".join(out)
