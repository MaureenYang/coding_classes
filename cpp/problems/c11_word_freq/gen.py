TITLE = "單字頻率統計"
TOPIC = "STL"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

import string

SEPS = " ,.;:!?'\"-()0123456789\t"


def text(rng, nwords, vocab, line_len=12):
    out = []
    for i in range(nwords):
        w = rng.choice(vocab)
        w = "".join(ch.upper() if rng.random() < 0.2 else ch for ch in w)
        out.append(w)
        out.append("\n" if rng.random() < 1 / line_len else "".join(rng.choice(SEPS) for _ in range(rng.randint(1, 2))))
    return "".join(out)


def manual_cases():
    return [
        ("sample", "3\nThe cat and the hat.\nTHE END -- isn't it?"),
        ("no_text", "5\n"),
        ("only_punctuation", "2\n123 !!! ... --- '''\n456"),
        ("k_larger_than_distinct", "100\nb a c a"),
        ("tie_break_alphabetical", "10\nzeta alpha mid alpha zeta mid beta"),
        ("case_insensitive", "3\nHello hello HELLO hElLo world WORLD"),
        ("letters_split_by_digits_and_apostrophes", "10\nabc123def don't rock'n'roll x-ray e-mail"),
        ("last_word_without_newline", "1\nfirst last"),
        ("one_long_word", "1\n" + "a" * 100000),
        ("many_distinct", "100000\n" + " ".join("".join(chr(97 + (i // 26 ** k) % 26) for k in range(4)) for i in range(150000))),
    ]


def random_case(rng, size):
    n, vs = {"small": (12, 5), "medium": (5000, 300)}.get(size, (300000, 20000))
    vocab = ["".join(rng.choice(string.ascii_lowercase[:6] if size == "small" else string.ascii_lowercase)
                     for _ in range(rng.randint(1, 8))) for _ in range(vs)]
    k = rng.choice([1, 3, 10, vs, 10 ** 5])
    return f"{k}\n" + text(rng, n, vocab)
