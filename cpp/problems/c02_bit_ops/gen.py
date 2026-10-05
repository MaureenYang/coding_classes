TITLE = "位元運算"
TOPIC = "位元運算子"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

MAX = 2 ** 64 - 1
UNARY = ["popcount", "lowbit", "highbit", "ctz", "ispow2"]
BINARY = ["set", "clear", "toggle", "test", "rotl"]


def fmt(qs):
    return f"{len(qs)}\n" + "\n".join(qs)


def interesting(rng):
    return rng.choice([0, 1, MAX, 2 ** 63, 2 ** 63 - 1, 2 ** 32, 2 ** 31, 2 ** 32 - 1,
                       rng.randint(0, MAX), 1 << rng.randint(0, 63), rng.randint(0, 255)])


def manual_cases():
    every = [f"{op} {x}" for op in UNARY for x in [0, 1, 2, 3, MAX, 2 ** 63, 2 ** 63 - 1, 2 ** 31, 2 ** 32]]
    return [
        ("sample", fmt(["popcount 13", "lowbit 12", "highbit 1", "set 0 63", "test 5 1", "ispow2 64",
                        "rotl 9223372036854775808 1"])),
        ("zero_and_max", fmt(every)),
        ("bit_63_needs_1ULL", fmt(["set 0 63", "test 9223372036854775808 63", "clear 18446744073709551615 63",
                                   "toggle 0 63", "set 0 31", "set 0 32", "test 4294967296 32"])),
        ("rotl_zero_shift", fmt(["rotl 12345 0", "rotl 0 0", f"rotl {MAX} 0", f"rotl {MAX} 17", "rotl 1 63",
                                 "rotl 9223372036854775808 63", "rotl 3 62"])),
        ("powers_of_two", fmt([f"ispow2 {1 << i}" for i in range(64)] + [f"ispow2 {(1 << i) + 1}" for i in range(2, 64)])),
        ("all_bits_of_max", fmt([f"test {MAX} {k}" for k in range(64)] + [f"clear {MAX} {k}" for k in range(64)])),
    ]


def random_case(rng, size):
    q = {"small": 10, "medium": 2000}.get(size, 200000)
    qs = []
    for _ in range(q):
        x = interesting(rng)
        if rng.random() < 0.4:
            qs.append(f"{rng.choice(UNARY)} {x}")
        else:
            qs.append(f"{rng.choice(BINARY)} {x} {rng.choice([0, 63, rng.randint(0, 63)])}")
    return fmt(qs)
