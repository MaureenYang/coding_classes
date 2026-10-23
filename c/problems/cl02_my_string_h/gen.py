TITLE = "自己寫 string.h"
TOPIC = "C 字串/指標"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def q(s):
    return s if s else '""'


def rand_str(rng, maxlen, alpha):
    return "".join(rng.choice(alpha) for _ in range(rng.randint(0, maxlen)))


def rand_op(rng, maxlen):
    alpha = rng.choice(["ab", "abc", "abcdefghijklmnopqrstuvwxyz0123456789"])
    k = rng.randrange(6)
    a = rand_str(rng, maxlen, alpha)
    if k == 0:
        return f"len {q(a)}"
    if k == 1:
        b = a[:rng.randint(0, len(a))] + rand_str(rng, 3, alpha) if rng.random() < 0.6 else rand_str(rng, maxlen, alpha)
        return f"cmp {q(a)} {q(b)}"
    if k == 2:
        return f"cat {q(a)} {q(rand_str(rng, maxlen, alpha))}"
    if k == 3:
        return f"chr {q(a)} {rng.choice(alpha)}"
    if k == 4:
        if a and rng.random() < 0.5:
            i = rng.randrange(len(a)); t = a[i:i + rng.randint(1, 5)]
        else:
            t = rand_str(rng, 4, alpha)
        return f"str {q(a)} {q(t)}"
    return f"rev {q(a)}"


def manual_cases():
    return [
        ("sample", fmt(["len hello", 'len ""', "cmp abc abd", "cmp ab abc", "cat foo bar", "chr banana n", "str banana nan", "rev abc"])),
        ("empty_strings", fmt(['len ""', 'cmp "" ""', 'cmp "" a', 'cmp a ""', 'cat "" ""', 'cat "" x', 'cat x ""',
                               'chr "" a', 'str "" ""', 'str "" a', 'str abc ""', 'rev ""'])),
        ("prefix_compare", fmt(["cmp ab abc", "cmp abc ab", "cmp abc abc", "cmp z a", "cmp a z", "cmp a0 a9", "cmp 9 a"])),
        ("chr_positions", fmt(["chr a a", "chr ba a", "chr abc c", "chr abc d", "chr aaaa a", "chr 0123456789 9"])),
        ("strstr_tricky", fmt(["str aab ab", "str aaab aab", "str abc abcd", "str abc abc", "str abababc ababc",
                               "str mississippi issip", "str mississippi ppi", "str aaaa b", "str a a"])),
        ("rev_lengths", fmt(["rev a", "rev ab", "rev abc", "rev abcd", "rev racecar", "rev 0123456789"])),
        ("max_length", fmt(["len " + "a" * 100, "cat " + "x" * 100 + " " + "y" * 100, "rev " + "ab" * 50,
                            "str " + "a" * 99 + "b " + "a" * 50 + "b", "cmp " + "a" * 100 + " " + "a" * 99 + "b"])),
    ]


def random_case(rng, size):
    n = {"small": 8, "medium": 2000}.get(size, 20000)
    maxlen = {"small": 6}.get(size, 100)
    return fmt([rand_op(rng, maxlen) for _ in range(n)])
