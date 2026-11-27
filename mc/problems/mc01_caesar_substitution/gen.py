import os

TITLE = "凱撒與替換密碼破解"
TOPIC = "替換密碼、頻率分析"
DIFFICULTY = "★★"
TIME_LIMIT = 1.0

FREQ = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
        6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074]
A = ord("A")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_english.txt"), encoding="utf-8") as f:
    CORPUS = " ".join(f.read().upper().split())
LOOP = CORPUS + " " + CORPUS + " " + CORPUS        # 繞回開頭，長的片段也取得到


def shift(text, k):
    return "".join(chr((ord(c) - A + k) % 26 + A) if "A" <= c <= "Z" else c for c in text)


def subst(text, key):
    return "".join(key[ord(c) - A] if "A" <= c <= "Z" else c for c in text)


def chi(text):
    cnt = [0] * 26
    for c in text:
        if "A" <= c <= "Z":
            cnt[ord(c) - A] += 1
    n = sum(cnt)
    return sum((cnt[i] - n * FREQ[i] / 100) ** 2 / (n * FREQ[i] / 100) for i in range(26))


def breakable(plain, k):
    """確認「卡方值最小的位移」就是正確答案，而且領先夠多（避免浮點誤差影響結果）。"""
    ct = shift(plain, k)
    scores = sorted((chi(shift(ct, -s)), s) for s in range(26))
    return scores[0][1] == k and scores[0][0] < 0.6 * scores[1][0]


def excerpt(rng, letters):
    while True:
        i = rng.randrange(len(CORPUS))
        while i > 0 and LOOP[i - 1] != " ":
            i += 1
        j, n = i, 0
        while n < letters:
            n += LOOP[j].isalpha()
            j += 1
        return LOOP[i:j]


def rand_key(rng):
    k = [chr(A + i) for i in range(26)]
    rng.shuffle(k)
    return "".join(k)


def break_query(rng, letters):
    while True:
        plain = excerpt(rng, letters)
        k = rng.randrange(26)
        if breakable(plain, k):
            return "BREAK " + shift(plain, k)


def manual_cases():
    import random
    rng = random.Random(1)
    sample_plain = "THE RIVER HAD BEEN RISING FOR THREE DAYS BEFORE ANYONE IN THE VILLAGE THOUGHT TO MOVE THE GRAIN."
    assert breakable(sample_plain, 3)
    key = "QWERTYUIOPASDFGHJKLZXCVBNM"
    sample = ["3",
              "ENC " + key + " HELLO, WORLD!",
              "DEC " + key + " ITSSG, VGKSR!",
              "BREAK " + shift(sample_plain, 3)]
    identity = "".join(chr(A + i) for i in range(26))
    rot = [p for p in [excerpt(rng, 200) for _ in range(40)] if breakable(p, 0)]
    return [
        ("sample", "\n".join(sample)),
        ("identity_key", f"2\nENC {identity} NOTHING CHANGES.\nDEC {identity} 123 ... !?"),
        ("shift_zero", "1\nBREAK " + rot[0]),
        ("shift_25", "1\nBREAK " + shift(rot[1], 25) if breakable(rot[1], 25) else "1\nBREAK " + shift(sample_plain, 25)),
        ("enc_then_dec", "2\nENC " + key + " " + excerpt(rng, 300) + "\nDEC " + key + " " + subst(excerpt(rng, 300), key)),
    ]


def random_case(rng, size):
    q = {"small": 3, "medium": 20}.get(size, 100)
    letters = {"small": 100, "medium": 300}.get(size, 1500)
    lines = [str(q)]
    for _ in range(q):
        t = rng.randrange(3)
        if t == 0:
            lines.append(break_query(rng, letters))
        else:
            key = rand_key(rng)
            plain = excerpt(rng, rng.randint(10, letters))
            lines.append(("ENC " + key + " " + plain) if t == 1 else ("DEC " + key + " " + subst(plain, key)))
    return "\n".join(lines)
